from typing import Any, Dict
from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI
from langchain.schema import BaseMessage
from src.config import get_settings

settings = get_settings()

def get_llm():
    if settings.llm_provider == "ollama":
        return Ollama(model=settings.ollama_model)
    elif settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY not configured")
        return ChatOpenAI(
            model=settings.openai_model,
            temperature=0.2,
            openai_api_key=settings.openai_api_key,
        )
    raise ValueError("Unsupported LLM provider") 

def call_llm(messages: list[BaseMessage]) -> str:
    llm = get_llm()
    response = llm(messages)
    return response.content if hasattr(response, "content") else str(response)