from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import ProcessRequest, IngestRequest, ProcessResponse, IngestResponse
from .db_ingestor import DBIngestor
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
def process_text_content(request: ProcessRequest):
    # This endpoint is temporarily disabled during architecture refactoring
    # ParseBase system will be integrated in future updates
    raise HTTPException(
        status_code=501, 
        detail="Processing endpoint temporarily unavailable during system refactoring. Please use ParseBase CSV parsers directly."
    )

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
