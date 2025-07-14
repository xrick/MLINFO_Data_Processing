from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import ProcessRequest, IngestRequest, ProcessResponse, IngestResponse
from .db_ingestor import DBIngestor
from .csv_processor2 import CSVProcessor2
import os
import re
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Data Processing API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

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
    return {"message": "Welcome to the Data Processing API"}

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
