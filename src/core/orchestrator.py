from typing import Any, Dict, List

from src.config import get_settings
from src.ingestion.preprocessor import clean_text, chunk_text
from src.llm.chains import run_architecture_chain
from src.retrieval.hybrid import (
    build_bft_documents,
    get_hybrid_retrieval_manager,
)
from src.retrieval.utils import extract_known_systems, unwrap_document

settings = get_settings()


def build_context(documents, known_systems):
    parts = []

    if known_systems:
         systems_block = ["KNOWN SYSTEMS:\n"]
         for sys in known_systems:
             alias_part = f" (alias: {sys['alias']})" if sys.get("alias") else ""
             systems_block.append(
                 f"- System ID: {sys['system_id']}, Name: {sys['system_name']}{alias_part}"
             )
         parts.append("\n".join(systems_block))

    for doc in documents:
        if isinstance(doc, str):
            text = doc
        else:
            _, text = unwrap_document(doc)
        if text:
            parts.append(text)

    return "\n\n---\n\n".join(parts)

def run_bft_analysis(bft_id: str, raw_text: str) -> Dict[str, Any]:
    cleaned = clean_text(raw_text)
    chunks = chunk_text(cleaned)

    documents = build_bft_documents(bft_id, chunks)
    hybrid_manager = get_hybrid_retrieval_manager()
    hybrid_manager.add_documents(documents, replace=True)

    retrieved_docs = hybrid_manager.retrieve(
        cleaned,
        k=settings.retrieval_top_k,
    )

    context_blocks = []
    for doc in retrieved_docs:
        doc_id = doc.metadata.get("doc_id", "unknown")
        source = doc.metadata.get("source", "unknown")
        context_blocks.append(f"[source={source} id={doc_id}]\n{doc.page_content}")

    known_systems = extract_known_systems(documents)
    context = build_context(context_blocks, known_systems)#"\n\n".join(context_blocks)

    llm_result = run_architecture_chain(cleaned, context)

    return {
        "bft_id": bft_id,
        "llm_result": llm_result,
        "retrieved_context": context,
        "retrieved_documents": [
            {
                "doc_id": doc.metadata.get("doc_id"),
                "source": doc.metadata.get("source"),
                "metadata": doc.metadata,
            }
            for doc in retrieved_docs
        ],
    }