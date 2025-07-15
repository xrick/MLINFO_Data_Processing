import os
import time
import duckdb
from typing import List, Dict, Any, Optional
from pymilvus import connections, Collection, utility
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

class RAGService:
    """
    RAG (Retrieval-Augmented Generation) 服務
    結合 DuckDB 結構化查詢和 Milvus 向量相似度搜尋
    """
    
    def __init__(self):
        self.MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
        self.MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
        self.DUCKDB_FILE = "sales_specs.db"
        self.COLLECTION_NAME = "sales_notebook_specs"
        self.EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
        self._embedding_model = None
        
        # 預設問題模板
        self.default_questions = [
            "比較 950 和 960 系列的差異",
            "有哪些型號支援 USB-C PD 快充？",
            "AMD B19-S FT6 的電源管理功能如何？",
            "APX819 FP7R2 是否支援雙通道記憶體？",
            "839 系列的顯示規格為何？",
            "哪些型號具備指紋辨識功能？"
        ]
    
    @property
    def embedding_model(self):
        """延遲載入嵌入模型"""
        if self._embedding_model is None:
            logger.info("載入 SentenceTransformer 模型...")
            self._embedding_model = SentenceTransformer(self.EMBEDDING_MODEL_NAME)
        return self._embedding_model
    
    def get_suggestions(self) -> List[str]:
        """獲取建議問題"""
        return self.default_questions
    
    def search_similar(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """使用 Milvus 進行向量相似度搜尋"""
        try:
            # 連接 Milvus
            connections.connect("default", host=self.MILVUS_HOST, port=self.MILVUS_PORT)
            
            if not utility.has_collection(self.COLLECTION_NAME):
                logger.warning(f"Collection '{self.COLLECTION_NAME}' 不存在")
                return []
            
            collection = Collection(self.COLLECTION_NAME)
            collection.load()
            
            # 生成查詢向量
            query_vector = self.embedding_model.encode([query]).tolist()
            
            # 執行相似度搜尋
            search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
            results = collection.search(
                data=query_vector,
                anns_field="embedding",
                param=search_params,
                limit=limit,
                output_fields=["modeltype", "modelname", "cpu", "gpu", "memory", "storage"]
            )
            
            # 格式化結果
            similar_items = []
            for hits in results:
                for hit in hits:
                    similar_items.append({
                        "score": float(hit.score),
                        "data": hit.entity.fields
                    })
            
            return similar_items
            
        except Exception as e:
            logger.error(f"向量搜尋失敗: {str(e)}")
            return []
    
    def search_structured(self, query: str) -> List[Dict[str, Any]]:
        """使用 DuckDB 進行結構化查詢"""
        try:
            # 分析查詢中的關鍵字
            keywords = self._extract_keywords(query)
            
            with duckdb.connect(database=self.DUCKDB_FILE, read_only=True) as con:
                # 檢查表是否存在
                table_check = con.execute("SELECT table_name FROM information_schema.tables WHERE table_name = 'specs'").fetchone()
                if not table_check:
                    logger.warning("DuckDB 'specs' 表不存在")
                    return []
                
                # 建構動態查詢
                where_conditions = []
                params = []
                
                for keyword in keywords:
                    if keyword.isdigit() and len(keyword) == 3:  # 型號數字
                        where_conditions.append("modeltype LIKE ?")
                        params.append(f"%{keyword}%")
                    else:  # 其他關鍵字
                        where_conditions.append("""
                            (modelname LIKE ? OR cpu LIKE ? OR gpu LIKE ? OR 
                             memory LIKE ? OR storage LIKE ? OR wireless LIKE ?)
                        """)
                        keyword_param = f"%{keyword}%"
                        params.extend([keyword_param] * 6)
                
                if where_conditions:
                    sql = f"""
                        SELECT * FROM specs 
                        WHERE {' OR '.join(where_conditions)}
                        LIMIT 10
                    """
                    results = con.execute(sql, params).fetchdf()
                else:
                    # 如果沒有關鍵字，返回最近的記錄
                    results = con.execute("SELECT * FROM specs LIMIT 5").fetchdf()
                
                return results.to_dict('records')
                
        except Exception as e:
            logger.error(f"結構化查詢失敗: {str(e)}")
            return []
    
    def _extract_keywords(self, query: str) -> List[str]:
        """從查詢中提取關鍵字"""
        import re
        
        # 移除常見停用詞
        stop_words = {'的', '和', '與', '或', '是', '有', '沒有', '什麼', '如何', '哪些', '比較'}
        
        # 提取中文、英文、數字
        keywords = re.findall(r'[\w\d]+', query)
        
        # 過濾停用詞和短詞
        filtered = [k for k in keywords if k not in stop_words and len(k) > 1]
        
        return filtered
    
    def generate_answer(self, query: str, sources: List[Dict[str, Any]]) -> str:
        """基於搜尋結果生成回答"""
        if not sources:
            return "抱歉，我沒有找到相關的筆記型電腦資訊。請嘗試更具體的查詢，例如型號名稱或特定規格。"
        
        # 簡單的回答生成邏輯
        if "比較" in query:
            return self._generate_comparison_answer(sources)
        elif any(word in query for word in ["支援", "有", "具備"]):
            return self._generate_feature_answer(query, sources)
        else:
            return self._generate_general_answer(sources)
    
    def _generate_comparison_answer(self, sources: List[Dict[str, Any]]) -> str:
        """生成比較回答"""
        if len(sources) < 2:
            return "我找到了相關資訊，但需要更多型號來進行比較。"
        
        answer = "根據資料庫資訊，以下是相關型號的比較：\n\n"
        for i, source in enumerate(sources[:3], 1):
            data = source.get('data', source)
            answer += f"{i}. **{data.get('modelname', '未知型號')}** (型號: {data.get('modeltype', 'N/A')})\n"
            answer += f"   - CPU: {data.get('cpu', '未提供')}\n"
            answer += f"   - GPU: {data.get('gpu', '未提供')}\n"
            answer += f"   - 記憶體: {data.get('memory', '未提供')}\n"
            answer += f"   - 儲存: {data.get('storage', '未提供')}\n\n"
        
        return answer
    
    def _generate_feature_answer(self, query: str, sources: List[Dict[str, Any]]) -> str:
        """生成功能特性回答"""
        answer = "根據查詢結果，以下型號符合您的需求：\n\n"
        
        for i, source in enumerate(sources[:5], 1):
            data = source.get('data', source)
            answer += f"{i}. **{data.get('modelname', '未知型號')}** (型號: {data.get('modeltype', 'N/A')})\n"
            
            # 根據查詢內容顯示相關資訊
            if "充電" in query or "PD" in query:
                answer += f"   - 電源: {data.get('battery', '未提供')}\n"
            if "記憶體" in query or "RAM" in query:
                answer += f"   - 記憶體: {data.get('memory', '未提供')}\n"
            if "顯示" in query or "螢幕" in query:
                answer += f"   - 顯示: {data.get('lcd', '未提供')}\n"
            
            answer += "\n"
        
        return answer
    
    def _generate_general_answer(self, sources: List[Dict[str, Any]]) -> str:
        """生成一般回答"""
        answer = "我找到了以下相關的筆記型電腦資訊：\n\n"
        
        for i, source in enumerate(sources[:3], 1):
            data = source.get('data', source)
            answer += f"{i}. **{data.get('modelname', '未知型號')}** (型號: {data.get('modeltype', 'N/A')})\n"
            answer += f"   主要規格: CPU {data.get('cpu', '未提供')}, GPU {data.get('gpu', '未提供')}\n\n"
        
        answer += "如需更詳細的資訊，請告訴我您想了解的具體規格。"
        return answer
    
    def query(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """執行完整的 RAG 查詢"""
        start_time = time.time()
        
        try:
            # 同時執行向量搜尋和結構化查詢
            similar_results = self.search_similar(query, max_results)
            structured_results = self.search_structured(query)
            
            # 合併和去重結果
            all_sources = []
            seen_models = set()
            
            # 添加向量搜尋結果
            for result in similar_results:
                model_id = f"{result['data'].get('modeltype', '')}-{result['data'].get('modelname', '')}"
                if model_id not in seen_models:
                    all_sources.append(result)
                    seen_models.add(model_id)
            
            # 添加結構化查詢結果
            for result in structured_results:
                model_id = f"{result.get('modeltype', '')}-{result.get('modelname', '')}"
                if model_id not in seen_models:
                    all_sources.append({"data": result, "score": 0.5})
                    seen_models.add(model_id)
            
            # 生成回答
            answer = self.generate_answer(query, all_sources)
            
            query_time = time.time() - start_time
            
            return {
                "answer": answer,
                "sources": all_sources[:max_results],
                "query_time": query_time,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"RAG 查詢失敗: {str(e)}")
            return {
                "answer": f"查詢過程中發生錯誤: {str(e)}",
                "sources": [],
                "query_time": time.time() - start_time,
                "success": False
            }
    
    def compare_models(self, model_names: List[str], compare_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """比較多個型號"""
        try:
            if not compare_fields:
                compare_fields = ["modeltype", "modelname", "cpu", "gpu", "memory", "storage", "battery", "wireless"]
            
            with duckdb.connect(database=self.DUCKDB_FILE, read_only=True) as con:
                # 建構查詢條件
                conditions = []
                params = []
                
                for model in model_names:
                    conditions.append("(modeltype LIKE ? OR modelname LIKE ?)")
                    params.extend([f"%{model}%", f"%{model}%"])
                
                if conditions:
                    sql = f"""
                        SELECT {', '.join(compare_fields)} FROM specs 
                        WHERE {' OR '.join(conditions)}
                        LIMIT 10
                    """
                    results = con.execute(sql, params).fetchdf()
                    
                    if results.empty:
                        return {
                            "comparison_table": [],
                            "summary": "未找到指定的型號資訊",
                            "success": False
                        }
                    
                    comparison_table = results.to_dict('records')
                    summary = f"成功比較了 {len(comparison_table)} 個型號的規格資訊"
                    
                    return {
                        "comparison_table": comparison_table,
                        "summary": summary,
                        "success": True
                    }
                else:
                    return {
                        "comparison_table": [],
                        "summary": "未提供有效的型號名稱",
                        "success": False
                    }
                    
        except Exception as e:
            logger.error(f"型號比較失敗: {str(e)}")
            return {
                "comparison_table": [],
                "summary": f"比較過程中發生錯誤: {str(e)}",
                "success": False
            }