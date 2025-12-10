from typing import Iterable, Dict, Any
import chromadb
from chromadb.config import Settings as ChromaSettings
from src.config import get_settings

settings = get_settings()
client = chromadb.Client(
    ChromaSettings(
        persist_directory=str(settings.chroma_path),
        anonymized_telemetry=False,
    )
)

def get_collection(name: str = "systems") -> chromadb.api.models.Collection.Collection:
    return client.get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})

def upsert_documents(
    collection_name: str,
    documents: Iterable[str],
    metadatas: Iterable[Dict[str, Any]],
    ids: Iterable[str],
) -> None:
    collection = get_collection(collection_name)
    collection.upsert(documents=list(documents), metadatas=list(metadatas), ids=list(ids))