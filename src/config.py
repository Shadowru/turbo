from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "BFT Semantic Analyzer"
    api_prefix: str = "/api/v1"

    # SQLite
    sqlite_path: Path = Field(default=Path("data/sqlite.db"))

    # Chroma
    chroma_path: Path = Field(default=Path("data/chroma"))

    # LLM
    llm_provider: str = Field(default="ollama")  # or "openai"
    ollama_model: str = Field(default="mistral")
    openai_model: str = Field(default="gpt-4.1-mini")
    openai_api_key: str | None = None

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()