from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "BFT Semantic Analyzer"
    api_prefix: str = "/api/v1"

    sqlite_path: Path = Field(default=Path("data/sqlite.db"))
    chroma_path: Path = Field(default=Path("data/chroma"))
    bm25_index_path: Path = Field(default=Path("data/bm25_index.json"))

    llm_provider: str = "ollama"  # или "openai"
    ollama_model: str = "gpt-oss:20b"
    openai_model: str = "gpt-4.1-mini"
    openai_api_url: str = "http://localhost:1143" 
    openai_api_key: str | None = None

    embedding_model_name: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    retrieval_top_k: int = Field(default=6)

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()