from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Iterable, List, Sequence

from langchain.retrievers import EnsembleRetriever
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import Chroma

from src.config import get_settings
from src.db import crud
from src.ingestion.preprocessor import clean_text, chunk_text

settings = get_settings()


@lru_cache()
def _get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=settings.embedding_model_name)


@lru_cache()
def _get_vectorstore(collection_name: str = "rag_corpus") -> Chroma:
    settings.chroma_path.mkdir(parents=True, exist_ok=True)
    return Chroma(
        collection_name=collection_name,
        embedding_function=_get_embeddings(),
        persist_directory=str(settings.chroma_path),
    )


def build_bft_documents(bft_id: str, chunks: Sequence[str]) -> List[Document]:
    doc_base_id = f"bft::{bft_id}"

    docs: List[Document] = []
    for idx, chunk in enumerate(chunks):
        doc_id = f"{doc_base_id}::{idx}"
        docs.append(
            Document(
                page_content=chunk,
                metadata={
                    "doc_id": doc_id,
                    "doc_base_id": doc_base_id,
                    "source": "bft",
                    "bft_id": bft_id,
                    "chunk_index": idx,
                },
            )
        )
    return docs


def build_system_documents() -> List[Document]:
    systems = crud.list_systems_full()
    docs: List[Document] = []

    for system in systems:
        doc_base_id = f"system::{system.system_id}"

        lines = [
            f"System ID: {system.system_id}",
            f"Name: {system.name}",
            f"Description: {system.description or '—'}",
            f"Domain: {system.domain or '—'}",
            f"Owner: {system.owner or '—'}",
        ]

        if system.interfaces:
            lines.append("Interfaces:")
            for iface in system.interfaces:
                lines.append(
                    f"- {iface.interface_type}: {iface.endpoint or '—'} ({iface.description or '—'})"
                )

        if system.topics:
            lines.append("Integration topics:")
            for topic in system.topics:
                direction = topic.direction or "n/a"
                lines.append(
                    f"- {topic.name} [{direction}] schema={topic.payload_schema or '—'}"
                )

        content = clean_text("\n".join(lines))
        chunks = chunk_text(content, max_tokens=400, overlap=40)
        for idx, chunk in enumerate(chunks):
            doc_id = f"{doc_base_id}::{idx}"
            docs.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "doc_id": doc_id,
                        "doc_base_id": doc_base_id,
                        "source": "system_registry",
                        "system_id": system.system_id,
                        "chunk_index": idx,
                    },
                )
            )
    return docs


def build_generic_documents(
    doc_id_base: str,
    source: str,
    text: str,
    extra_metadata: dict | None = None,
) -> List[Document]:
    doc_base_id = f"rag::{source}::{doc_id_base}"
    cleaned = clean_text(text)
    chunks = chunk_text(cleaned, max_tokens=400, overlap=40)

    docs: List[Document] = []
    reserved_keys = {"doc_id", "doc_base_id", "chunk_index", "source"}

    for idx, chunk in enumerate(chunks):
        doc_id = f"{doc_base_id}::{idx}"
        metadata = {
            "doc_id": doc_id,
            "doc_base_id": doc_base_id,
            "source": source,
            "chunk_index": idx,
        }
        if extra_metadata:
            for key, value in extra_metadata.items():
                if key not in reserved_keys:
                    metadata[key] = value

        docs.append(
            Document(
                page_content=chunk,
                metadata=metadata,
            )
        )

    return docs


class HybridRetrievalManager:
    def __init__(self) -> None:
        self._vectorstore = _get_vectorstore()
        self._bm25_index_path: Path = settings.bm25_index_path
        self._bm25_index_path.parent.mkdir(parents=True, exist_ok=True)

        self._documents: List[Document] = self._load_documents()
        self._doc_index: dict[str, int] = {}
        self._rebuild_doc_index()

        self._bm25: BM25Retriever | None = None
        self._rebuild_bm25()

        # начальная синхронизация реестра систем
        self.ensure_system_documents()

    def add_documents(self, docs: Iterable[Document], replace: bool = False) -> None:
        docs = list(docs)
        if not docs:
            return

        if replace:
            base_ids = {
                doc.metadata.get("doc_base_id")
                for doc in docs
                if doc.metadata.get("doc_base_id")
            }
            for base_id in base_ids:
                self._remove_documents_by_base(base_id)

        new_docs: List[Document] = []
        new_ids: List[str] = []

        for doc in docs:
            doc_id = doc.metadata.get("doc_id")
            if not doc_id:
                continue
            if doc_id in self._doc_index:
                # уже существует — пропускаем
                continue
            new_docs.append(doc)
            new_ids.append(doc_id)

        if not new_docs:
            return

        self._documents.extend(new_docs)
        self._rebuild_doc_index()
        self._vectorstore.add_documents(new_docs, ids=new_ids)
        self._vectorstore.persist()
        self._rebuild_bm25()
        self._save_documents()

    def ensure_system_documents(self) -> None:
        system_docs = build_system_documents()
        self.add_documents(system_docs, replace=True)

    def retrieve(
        self,
        query: str,
        k: int = 5,
        weights: tuple[float, float] = (0.4, 0.6),
    ) -> List[Document]:
        retrievers = []
        weights_list = []

        if self._bm25 and self._documents:
            self._bm25.k = k
            retrievers.append(self._bm25)
            weights_list.append(weights[0])

        vector_retriever = self._vectorstore.as_retriever(search_kwargs={"k": k})
        retrievers.append(vector_retriever)
        weights_list.append(weights[-1])

        if len(retrievers) == 1:
            docs = retrievers[0].invoke(query)
        else:
            ensemble = EnsembleRetriever(retrievers=retrievers, weights=weights_list)
            docs = ensemble.invoke(query)

        unique_docs: List[Document] = []
        seen_ids: set[str] = set()

        for doc in docs:
            doc_id = doc.metadata.get("doc_id")
            if doc_id and doc_id in seen_ids:
                continue
            if doc_id:
                seen_ids.add(doc_id)
            unique_docs.append(doc)

        return unique_docs[:k]

    # --- внутренние методы ---

    def _remove_documents_by_base(self, base_id: str | None) -> None:
        if not base_id:
            return

        ids_to_remove = [
            doc.metadata.get("doc_id")
            for doc in self._documents
            if doc.metadata.get("doc_base_id") == base_id
        ]
        ids_to_remove = [doc_id for doc_id in ids_to_remove if doc_id]

        if not ids_to_remove:
            return

        self._documents = [
            doc
            for doc in self._documents
            if doc.metadata.get("doc_base_id") != base_id
        ]

        self._vectorstore.delete(ids=ids_to_remove)
        self._vectorstore.persist()

        self._rebuild_doc_index()
        self._rebuild_bm25()
        self._save_documents()

    def _rebuild_doc_index(self) -> None:
        self._doc_index = {}
        for idx, doc in enumerate(self._documents):
            doc_id = doc.metadata.get("doc_id", f"idx::{idx}")
            self._doc_index[doc_id] = idx

    def _rebuild_bm25(self) -> None:
        if not self._documents:
            self._bm25 = None
            return
        self._bm25 = BM25Retriever.from_documents(self._documents)

    def _save_documents(self) -> None:
        payload = [
            {"page_content": doc.page_content, "metadata": doc.metadata}
            for doc in self._documents
        ]
        self._bm25_index_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _load_documents(self) -> List[Document]:
        if not self._bm25_index_path.exists():
            return []
        raw = json.loads(self._bm25_index_path.read_text(encoding="utf-8"))
        return [
            Document(page_content=item["page_content"], metadata=item.get("metadata", {}))
            for item in raw
        ]


@lru_cache()
def get_hybrid_retrieval_manager() -> HybridRetrievalManager:
    return HybridRetrievalManager()