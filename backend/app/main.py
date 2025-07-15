from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import (
    ProcessRequest, IngestRequest, ProcessResponse, IngestResponse,
    ChatQueryRequest, ChatQueryResponse, CompareRequest, CompareResponse,
    SystemHealthResponse, SystemStatsResponse
)
from .db_ingestor import DBIngestor
from .csv_processor2 import CSVProcessor2
from .rag_service import RAGService
from .system_service import SystemService
import os
import re
from dotenv import load_dotenv
from typing import List

load_dotenv()

app = FastAPI(
    title="SalesRAG - 筆記型電腦智能銷售系統", 
    version="3.0.0",
    description="整合資料處理與智能問答的統一平台"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# 初始化服務
rag_service = RAGService()
system_service = SystemService()

def validate_regex_patterns(patterns):
    """Validate regex patterns for safety"""
    if not patterns:
        return True
    
    for pattern in patterns:
        if not pattern.strip():
            continue
        try:
            re.compile(pattern)
        except re.error:
            return False
    return True

@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "歡迎使用 SalesRAG 筆記型電腦智能銷售系統",
        "version": "3.0.0",
        "features": ["資料處理", "智能問答", "規格比較", "系統監控"]
    }

@app.post("/api/process", response_model=ProcessResponse, tags=["Processing"])
def process_csv_content(request: ProcessRequest):
    """
    處理 CSV 內容並返回解析結果 (使用 CSVProcessor2 strategy pattern)
    支援三階段 modeltype 判斷：檔名→內容→用戶輸入
    """
    try:
        # 驗證輸入
        if not request.text_content.strip():
            raise HTTPException(status_code=400, detail="CSV content cannot be empty.")
        if request.temp_regex and not validate_regex_patterns(request.temp_regex):
            raise HTTPException(status_code=400, detail="Invalid regex patterns provided.")
        processor = CSVProcessor2()
        result = processor.process_csv_content(
            csv_content=request.text_content,
            custom_rules=request.custom_rules
        )
        # 三階段 modeltype 判斷
        modeltype = None
        # 1. 檔名
        if request.file_name:
            modeltype = processor.detect_modeltype(request.file_name, result)
        # 2. 內容
        if not modeltype:
            modeltype = processor.detect_modeltype("", result)
        # 3. 用戶輸入
        if not modeltype and request.user_modeltype:
            modeltype = request.user_modeltype.strip()
        # 若仍無法判斷，要求前端輸入
        if not modeltype:
            return {"require_modeltype_input": True, "data": result}
        # 補齊所有資料的 modeltype 欄位
        for row in result:
            if isinstance(row, dict):
                row["modeltype"] = modeltype
        return {"data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV processing failed: {str(e)}")

@app.post("/api/ingest-to-db", response_model=IngestResponse, tags=["Database"])
def ingest_data_to_db(request: IngestRequest):
    if not request.data:
        raise HTTPException(status_code=400, detail="data cannot be empty.")
    try:
        ingestor = DBIngestor()
        duckdb_count, milvus_count = ingestor.ingest(request.data)
        return IngestResponse(
            success=True,
            message="Data ingestion successful.",
            duckdb_rows_added=duckdb_count,
            milvus_entities_added=milvus_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# RAG 查詢 API
@app.post("/api/chat/query", response_model=ChatQueryResponse, tags=["RAG"])
def chat_query(request: ChatQueryRequest):
    """
    智能問答查詢端點
    支援自然語言查詢筆記型電腦規格資訊
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
        # 記錄查詢統計
        system_service.record_query(request.query)
        
        # 執行 RAG 查詢
        result = rag_service.query(request.query, request.max_results)
        
        return ChatQueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            query_time=result["query_time"],
            success=result["success"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢失敗: {str(e)}")

@app.get("/api/chat/suggestions", tags=["RAG"])
def get_chat_suggestions() -> List[str]:
    """
    獲取建議問題列表
    """
    try:
        return rag_service.get_suggestions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取建議失敗: {str(e)}")

@app.post("/api/chat/compare", response_model=CompareResponse, tags=["RAG"])
def compare_models(request: CompareRequest):
    """
    比較多個筆記型電腦型號
    """
    try:
        if not request.models or len(request.models) < 2:
            raise HTTPException(status_code=400, detail="至少需要提供兩個型號進行比較")
        
        result = rag_service.compare_models(request.models, request.compare_fields)
        
        return CompareResponse(
            comparison_table=result["comparison_table"],
            summary=result["summary"],
            success=result["success"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"比較失敗: {str(e)}")

# 系統狀態 API
@app.get("/api/system/health", response_model=SystemHealthResponse, tags=["System"])
def get_system_health():
    """
    獲取系統健康狀態
    """
    try:
        health = system_service.get_health_status()
        return SystemHealthResponse(
            status=health["status"],
            duckdb_status=health["duckdb_status"],
            milvus_status=health["milvus_status"],
            total_records=health["total_records"],
            last_update=health["last_update"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"健康檢查失敗: {str(e)}")

@app.get("/api/system/stats", response_model=SystemStatsResponse, tags=["System"])
def get_system_stats():
    """
    獲取系統使用統計
    """
    try:
        stats = system_service.get_system_stats()
        return SystemStatsResponse(
            total_queries=stats["total_queries"],
            total_records=stats["total_records"],
            database_size=stats["database_size"],
            popular_queries=stats["popular_queries"],
            success=stats["success"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取統計失敗: {str(e)}")

@app.post("/api/system/clean", tags=["System"])
def clean_system_data():
    """
    清理所有系統資料
    """
    try:
        result = system_service.clean_all_data()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"資料清理失敗: {str(e)}")

@app.get("/api/data-status", tags=["System"])
def get_data_status():
    """
    獲取資料庫狀態概覽
    """
    try:
        health = system_service.get_health_status()
        return {
            "total_records": health["total_records"],
            "last_update": health["last_update"],
            "duckdb_healthy": health["duckdb_status"] == "healthy",
            "milvus_healthy": health["milvus_status"] == "healthy"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取資料狀態失敗: {str(e)}")
