from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel
from typing import Literal
from datetime import datetime

class BFTRequest(BaseModel):
    bft_id: str
    text: str

class BFTResponse(BaseModel):
    bft_id: str
    structured_output: Dict[str, Any]
    artifacts: Dict[str, Any]
    history_id: int
    created_at: datetime
    
class RAGDocumentRequest(BaseModel):
    doc_id: str
    source: str = "external"
    text: str
    metadata: Dict[str, Any] | None = None

class RAGDocumentResponse(BaseModel):
    status: Literal["ok"] = "ok"
    doc_id: str
    source: str
    chunks_added: int
    
class HistoryItem(BaseModel):
    id: int
    bft_id: str
    created_at: datetime
    preview: str

class HistoryListResponse(BaseModel):
    items: list[HistoryItem]

class HistoryDetailResponse(BaseModel):
    id: int
    bft_id: str
    request_text: str
    structured_output: Dict[str, Any]
    artifacts: Dict[str, Any]
    raw_llm_output: Optional[str]
    retrieved_context: Optional[str]
    created_at: datetime    
    
class RagUploadedDocument(BaseModel):
    doc_id: str
    filename: str
    size_bytes: int
    status: Literal["processed", "pending", "error"] = "processed"
    uploaded_at: datetime


class RagUploadResponse(BaseModel):
    documents: list[RagUploadedDocument]    