from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import ProcessRequest, IngestRequest, ProcessResponse, IngestResponse
from .parser import Parser
from .db_ingestor import DBIngestor
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Data Processing API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Data Processing API"}

@app.post("/api/process", response_model=ProcessResponse, tags=["Processing"])
def process_text_content(request: ProcessRequest):
    if not request.text_content.strip():
        raise HTTPException(status_code=400, detail="text_content cannot be empty.")
    try:
        parser_engine = Parser(request)
        processed_data = parser_engine.run()
        if not processed_data:
            return ProcessResponse(data=[], error="Could not extract any models.")
        return ProcessResponse(data=processed_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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