from typing import Dict, Any
from src.ingestion.preprocessor import clean_text, chunk_text
from src.ingestion.rag_loader import upsert_documents, get_collection
from src.llm.chains import run_architecture_chain

def run_bft_analysis(bft_id: str, raw_text: str) -> Dict[str, Any]:
    cleaned = clean_text(raw_text)
    chunks = chunk_text(cleaned)

    # Обновляем векторное хранилище (в MVP напрямую)
    upsert_documents(
        collection_name="bft_documents",
        documents=chunks,
        metadatas=[{"bft_id": bft_id}] * len(chunks),
        ids=[f"{bft_id}-{i}" for i in range(len(chunks))],
    )

    # Получаем контекст (пока простой top-k)
    collection = get_collection("systems")
    retrieved = collection.query(query_texts=[cleaned], n_results=5)

    context = ""
    if retrieved["documents"]:
        context = "\n\n".join(doc for docs in retrieved["documents"] for doc in docs)

    llm_result = run_architecture_chain(cleaned, context)

    return {
        "bft_id": bft_id,
        "llm_result": llm_result,
        "retrieved_context": context,
    }