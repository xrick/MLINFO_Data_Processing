#!/usr/bin/env python3
"""
Milvus 檢視器
用於檢視 sales_notebook_specs 集合中的資料
"""

import os
import sys
import numpy as np
from pymilvus import connections, utility, Collection
from pathlib import Path

class MilvusViewer:
    def __init__(self):
        self.MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
        self.MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
        self.COLLECTION_NAME = "sales_notebook_specs"
        self.ALL_FIELDS = [
            'modeltype', 'version', 'modelname', 'mainboard', 'devtime', 'pm', 
            'structconfig', 'lcd', 'touchpanel', 'iointerface', 'ledind', 
            'powerbutton', 'keyboard', 'webcamera', 'touchpad', 'fingerprint', 
            'audio', 'battery', 'cpu', 'gpu', 'memory', 'lcdconnector', 'storage', 
            'wifislot', 'thermal', 'tpm', 'rtc', 'wireless', 'lan', 'bluetooth', 
            'softwareconfig', 'ai', 'accessory', 'certifications', 'otherfeatures'
        ]
        
    def connect_to_milvus(self):
        """連接到 Milvus"""
        try:
            print(f"🔄 連接到 Milvus: {self.MILVUS_HOST}:{self.MILVUS_PORT}")
            connections.connect("default", host=self.MILVUS_HOST, port=self.MILVUS_PORT)
            print("✅ Milvus 連線成功")
            return True
        except Exception as e:
            print(f"❌ Milvus 連線失敗: {e}")
            return False
    
    def check_collection_exists(self):
        """檢查集合是否存在"""
        try:
            if not utility.has_collection(self.COLLECTION_NAME):
                print(f"❌ 集合不存在: {self.COLLECTION_NAME}")
                return False
            print(f"✅ 集合存在: {self.COLLECTION_NAME}")
            return True
        except Exception as e:
            print(f"❌ 檢查集合失敗: {e}")
            return False
    
    def get_collection_info(self):
        """取得集合資訊"""
        try:
            collection = Collection(self.COLLECTION_NAME)
            collection.load()
            
            # 取得集合統計資訊
            stats = collection.get_statistics()
            print(f"📊 集合統計: {stats}")
            
            # 取得集合結構
            schema = collection.schema
            print(f"📋 集合結構: {schema}")
            
            return collection
        except Exception as e:
            print(f"❌ 取得集合資訊失敗: {e}")
            return None
    
    def get_entity_count(self):
        """取得實體數量"""
        try:
            collection = Collection(self.COLLECTION_NAME)
            collection.load()
            count = collection.num_entities
            return count
        except Exception as e:
            print(f"❌ 取得實體數量失敗: {e}")
            return 0
    
    def get_all_entities(self, limit=None):
        """取得所有實體"""
        try:
            collection = Collection(self.COLLECTION_NAME)
            collection.load()
            
            # 準備查詢表達式
            if limit:
                query_expr = f"pk >= 0 and pk < {limit}"
            else:
                query_expr = "pk >= 0"
            
            # 查詢資料
            results = collection.query(
                expr=query_expr,
                output_fields=self.ALL_FIELDS + ['pk'],
                limit=limit if limit else 1000  # 預設限制 1000 筆
            )
            
            return results
        except Exception as e:
            print(f"❌ 取得實體失敗: {e}")
            return []
    
    def get_entities_by_modeltype(self, modeltype):
        """根據 modeltype 查詢實體"""
        try:
            collection = Collection(self.COLLECTION_NAME)
            collection.load()
            
            # 查詢特定 modeltype 的資料
            query_expr = f'modeltype == "{modeltype}"'
            results = collection.query(
                expr=query_expr,
                output_fields=self.ALL_FIELDS + ['pk'],
                limit=1000
            )
            
            return results
        except Exception as e:
            print(f"❌ 查詢實體失敗: {e}")
            return []
    
    def search_similar_entities(self, search_text, top_k=5):
        """搜尋相似實體"""
        try:
            from sentence_transformers import SentenceTransformer
            
            # 載入嵌入模型
            model_name = "all-MiniLM-L6-v2"
            print(f"🔄 載入嵌入模型: {model_name}")
            model = SentenceTransformer(model_name)
            
            # 生成搜尋向量
            search_vector = model.encode([search_text])
            
            collection = Collection(self.COLLECTION_NAME)
            collection.load()
            
            # 向量搜尋
            search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
            results = collection.search(
                data=search_vector,
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                output_fields=self.ALL_FIELDS
            )
            
            return results
        except Exception as e:
            print(f"❌ 向量搜尋失敗: {e}")
            return []
    
    def display_collection_summary(self):
        """顯示集合摘要"""
        print("=" * 80)
        print("📊 Milvus 集合摘要")
        print("=" * 80)
        
        if not self.connect_to_milvus():
            return
        
        if not self.check_collection_exists():
            return
        
        # 取得實體數量
        count = self.get_entity_count()
        print(f"📈 總實體數: {count}")
        
        if count == 0:
            print("📭 集合中沒有實體")
            return
        
        # 取得集合資訊
        collection = self.get_collection_info()
        if collection:
            print(f"📋 欄位數: {len(self.ALL_FIELDS)}")
            print(f"🔍 向量維度: 384 (embedding 欄位)")
    
    def display_all_entities(self, limit=10):
        """顯示所有實體"""
        print("\n" + "=" * 80)
        print(f"📋 顯示前 {limit} 個實體")
        print("=" * 80)
        
        if not self.connect_to_milvus():
            return
        
        entities = self.get_all_entities(limit)
        
        if not entities:
            print("📭 沒有實體可顯示")
            return
        
        # 顯示實體
        for i, entity in enumerate(entities, 1):
            print(f"\n📄 實體 {i} (pk: {entity.get('pk', 'N/A')}):")
            print("-" * 40)
            for field in self.ALL_FIELDS:
                value = entity.get(field, '')
                # 限制顯示長度
                display_value = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                print(f"  {field:<20}: {display_value}")
    
    def display_entities_by_modeltype(self, modeltype):
        """顯示特定 modeltype 的實體"""
        print(f"\n" + "=" * 80)
        print(f"📋 顯示 modeltype = '{modeltype}' 的實體")
        print("=" * 80)
        
        if not self.connect_to_milvus():
            return
        
        entities = self.get_entities_by_modeltype(modeltype)
        
        if not entities:
            print(f"📭 沒有找到 modeltype = '{modeltype}' 的實體")
            return
        
        print(f"📈 找到 {len(entities)} 個實體")
        
        # 顯示實體
        for i, entity in enumerate(entities, 1):
            print(f"\n📄 實體 {i} (pk: {entity.get('pk', 'N/A')}):")
            print("-" * 40)
            for field in self.ALL_FIELDS:
                value = entity.get(field, '')
                # 限制顯示長度
                display_value = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                print(f"  {field:<20}: {display_value}")
    
    def display_similar_search(self, search_text, top_k=5):
        """顯示相似搜尋結果"""
        print(f"\n" + "=" * 80)
        print(f"🔍 搜尋相似實體: '{search_text}'")
        print("=" * 80)
        
        if not self.connect_to_milvus():
            return
        
        results = self.search_similar_entities(search_text, top_k)
        
        if not results:
            print("📭 沒有找到相似實體")
            return
        
        print(f"📈 找到 {len(results[0])} 個相似實體")
        
        # 顯示搜尋結果
        for i, hit in enumerate(results[0], 1):
            print(f"\n📄 相似實體 {i} (距離: {hit.distance:.4f}):")
            print("-" * 40)
            for field in self.ALL_FIELDS:
                value = hit.entity.get(field, '')
                # 限制顯示長度
                display_value = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                print(f"  {field:<20}: {display_value}")
    
    def export_to_json(self, filename="milvus_export.json"):
        """匯出資料到 JSON 檔案"""
        try:
            if not self.connect_to_milvus():
                return
            
            entities = self.get_all_entities()
            
            if not entities:
                print("📭 沒有資料可匯出")
                return
            
            import json
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(entities, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 資料已匯出到: {filename}")
            print(f"📊 匯出實體數: {len(entities)}")
        except Exception as e:
            print(f"❌ 匯出失敗: {e}")
    
    def interactive_mode(self):
        """互動模式"""
        while True:
            print("\n" + "=" * 50)
            print("🔍 Milvus 檢視器 - 互動模式")
            print("=" * 50)
            print("1. 顯示集合摘要")
            print("2. 顯示所有實體 (前10個)")
            print("3. 顯示所有實體 (自訂數量)")
            print("4. 根據 modeltype 查詢")
            print("5. 向量相似搜尋")
            print("6. 匯出資料到 JSON")
            print("7. 退出")
            print("-" * 50)
            
            choice = input("請選擇選項 (1-7): ").strip()
            
            if choice == "1":
                self.display_collection_summary()
            elif choice == "2":
                self.display_all_entities(10)
            elif choice == "3":
                try:
                    limit = int(input("請輸入要顯示的實體數量: "))
                    self.display_all_entities(limit)
                except ValueError:
                    print("❌ 請輸入有效的數字")
            elif choice == "4":
                modeltype = input("請輸入 modeltype (如: 960, 928): ").strip()
                if modeltype:
                    self.display_entities_by_modeltype(modeltype)
                else:
                    print("❌ 請輸入有效的 modeltype")
            elif choice == "5":
                search_text = input("請輸入搜尋文字: ").strip()
                if search_text:
                    try:
                        top_k = int(input("請輸入要顯示的結果數量 (預設: 5): ") or "5")
                        self.display_similar_search(search_text, top_k)
                    except ValueError:
                        print("❌ 請輸入有效的數字")
                else:
                    print("❌ 請輸入搜尋文字")
            elif choice == "6":
                filename = input("請輸入 JSON 檔案名稱 (預設: milvus_export.json): ").strip()
                if not filename:
                    filename = "milvus_export.json"
                self.export_to_json(filename)
            elif choice == "7":
                print("👋 再見！")
                break
            else:
                print("❌ 無效選項，請重新選擇")

def main():
    """主函數"""
    viewer = MilvusViewer()
    
    # 檢查命令列參數
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "summary":
            viewer.display_collection_summary()
        elif command == "list":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            viewer.display_all_entities(limit)
        elif command == "search":
            if len(sys.argv) > 2:
                modeltype = sys.argv[2]
                viewer.display_entities_by_modeltype(modeltype)
            else:
                print("❌ 請提供 modeltype 參數")
        elif command == "similar":
            if len(sys.argv) > 2:
                search_text = sys.argv[2]
                top_k = int(sys.argv[3]) if len(sys.argv) > 3 else 5
                viewer.display_similar_search(search_text, top_k)
            else:
                print("❌ 請提供搜尋文字參數")
        elif command == "export":
            filename = sys.argv[2] if len(sys.argv) > 2 else "milvus_export.json"
            viewer.export_to_json(filename)
        else:
            print("❌ 無效命令")
            print("可用命令: summary, list [limit], search <modeltype>, similar <text> [top_k], export [filename]")
    else:
        # 互動模式
        viewer.interactive_mode()

if __name__ == "__main__":
    main() 