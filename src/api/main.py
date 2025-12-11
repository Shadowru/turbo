import logging
import traceback

from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
from datetime import datetime

from src.api.schemas import BFTRequest, BFTResponse, RAGDocumentRequest, RAGDocumentResponse, HistoryListResponse, HistoryDetailResponse, RagUploadResponse

from src.core.pipeline import process_bft
from src.db.base import init_db
from src.config import get_settings
from src.retrieval.hybrid import (
    build_generic_documents,
    get_hybrid_retrieval_manager,
)
from src.db import crud
from langchain_core.documents import Document


logging.basicConfig(filename='./tmp/app.log', level=logging.INFO)

settings = get_settings()
app = FastAPI(title=settings.app_name)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

@app.post(f"{settings.api_prefix}/analyze", response_model=BFTResponse)
def analyze_bft(request: BFTRequest):
    try:
        result = process_bft(bft_id=request.bft_id, text=request.text)
        
        history_entry = crud.create_history_entry(
            bft_id=request.bft_id,
            request_text=request.text,
            structured_output=result.structured_output,
            artifacts=result.artifacts,
            raw_llm_output=result.raw_llm_output,
            retrieved_context=result.retrieved_context,
        )
        
        return BFTResponse(
            bft_id=request.bft_id,
            structured_output=result.structured_output,
            artifacts=result.artifacts,
            history_id=history_entry.id,
            created_at=history_entry.created_at
        )
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    
@app.post(f"{settings.api_prefix}/rag/documents/ingest", response_model=RAGDocumentResponse)
def ingest_rag_document(request: RAGDocumentRequest):
    try:
        manager = get_hybrid_retrieval_manager()
        docs = build_generic_documents(
            doc_id_base=request.doc_id,
            source=request.source,
            text=request.text,
            extra_metadata=request.metadata,
        )
        manager.add_documents(docs, replace=True)

        return RAGDocumentResponse(
            doc_id=request.doc_id,
            source=request.source,
            chunks_added=len(docs),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc    
    
@app.get(f"{settings.api_prefix}/history", response_model=HistoryListResponse)
def get_history(limit: int = Query(20, ge=1, le=100), bft_id: str | None = None):
    items = crud.list_history(limit=limit, bft_id=bft_id)
    result = []
    for item in items:
        preview = item.request_text[:160].replace("\n", " ")
        if len(item.request_text) > 160:
            preview += "..."
        result.append(
            {
                "id": item.id,
                "bft_id": item.bft_id,
                "created_at": item.created_at,
                "preview": preview,
            }
        )
    return HistoryListResponse(items=result)


@app.get(f"{settings.api_prefix}/history/latest", response_model=HistoryDetailResponse | None)
def get_latest(bft_id: str | None = None):
    entry = crud.get_latest_history(bft_id=bft_id)
    if not entry:
        return None
    return HistoryDetailResponse(
        id=entry.id,
        bft_id=entry.bft_id,
        request_text=entry.request_text,
        structured_output=entry.structured_output,
        artifacts=entry.artifacts,
        raw_llm_output=entry.raw_llm_output,
        retrieved_context=entry.retrieved_context,
        created_at=entry.created_at,
    )


@app.get(f"{settings.api_prefix}/history/{{history_id}}", response_model=HistoryDetailResponse)
def get_history_detail(history_id: int):
    entry = crud.get_history_by_id(history_id)
    if not entry:
        raise HTTPException(status_code=404, detail="History entry not found")
    return HistoryDetailResponse(
        id=entry.id,
        bft_id=entry.bft_id,
        request_text=entry.request_text,
        structured_output=entry.structured_output,
        artifacts=entry.artifacts,
        raw_llm_output=entry.raw_llm_output,
        retrieved_context=entry.retrieved_context,
        created_at=entry.created_at,
    )
    
@app.post(f"{settings.api_prefix}/rag/documents", response_model=RagUploadResponse)
async def upload_rag_documents(
    files: list[UploadFile] = File(default_factory=list),
    text: str = Form(default=""),
    auto_process: bool = Form(default=True),
):
    if not files and not text.strip():
        raise HTTPException(status_code=400, detail="Нужно передать файл или текст.")

    retrieval_manager = get_hybrid_retrieval_manager()
    ingested: list[dict[str, Any]] = []

    for upload in files:
        content = await upload.read()
        doc_id = f"doc-{uuid4().hex}"

        retrieval_manager.add_documents(
            [
                Document(
                    page_content=content.decode("utf-8", errors="ignore"),
                    metadata={
                        "doc_id": doc_id,
                        "filename": upload.filename,
                        "ingested_at": datetime.utcnow().isoformat(),
                        "source": "file_upload",
                    },
                )
            ]
        )

        ingested.append(
            {
                "doc_id": doc_id,
                "filename": upload.filename,
                "size_bytes": len(content),
                "status": "processed" if auto_process else "pending",
                "uploaded_at": datetime.utcnow(),
            }
        )

    if text.strip():
        doc_id = f"text-{uuid4().hex}"
        retrieval_manager.add_documents(
            [
                Document(
                    page_content=text,
                    metadata={
                        "doc_id": doc_id,
                        "filename": "manual_text.md",
                        "ingested_at": datetime.utcnow().isoformat(),
                        "source": "manual_text",
                    },
                )
            ]
        )
        ingested.append(
            {
                "doc_id": doc_id,
                "filename": "manual_text.md",
                "size_bytes": len(text.encode("utf-8")),
                "status": "processed" if auto_process else "pending",
                "uploaded_at": datetime.utcnow(),
            }
        )

    return RagUploadResponse(documents=ingested)    
    

@app.post(f"{settings.api_prefix}/rag/documents/text", response_model=RagUploadResponse)
async def upload_rag_documents(
    text: str = Form(default=""),
    auto_process: bool = Form(default=True),
):
    retrieval_manager = get_hybrid_retrieval_manager()
    ingested: list[dict[str, Any]] = []

    if text.strip():
        doc_id = f"text-{uuid4().hex}"
        retrieval_manager.add_documents(
            [
                Document(
                    page_content=text,
                    metadata={
                        "doc_id": doc_id,
                        "filename": "manual_text.md",
                        "ingested_at": datetime.utcnow().isoformat(),
                        "source": "manual_text",
                    },
                )
            ]
        )
        ingested.append(
            {
                "doc_id": doc_id,
                "filename": "manual_text.md",
                "size_bytes": len(text.encode("utf-8")),
                "status": "processed" if auto_process else "pending",
                "uploaded_at": datetime.utcnow(),
            }
        )

    return RagUploadResponse(documents=ingested)    
    
