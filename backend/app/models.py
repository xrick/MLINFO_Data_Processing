from pydantic import BaseModel
from typing import List, Dict, Optional

class ProcessRequest(BaseModel):
    text_content: str
    custom_rules: Optional[Dict[str, List[str]]] = None
    temp_regex: Optional[List[str]] = None

class ProcessResponse(BaseModel):
    data: List[Dict[str, str]]
    error: Optional[str] = None

class IngestRequest(BaseModel):
    data: List[Dict[str, str]]

class IngestResponse(BaseModel):
    success: bool
    message: str
    duckdb_rows_added: int
    milvus_entities_added: int
