import logging

from typing import List
from langchain_core.messages import BaseMessage

from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI

from src.config import get_settings

logger = logging.getLogger(__name__)


settings = get_settings()

def get_llm():
    if settings.llm_provider == "ollama":
        return ChatOllama(model=settings.ollama_model, temperature=0.2)
    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY not configured")
        return ChatOpenAI(
            base_url=settings.openai_api_url,
            model=settings.openai_model,
            temperature=0.2,
            api_key=settings.openai_api_key,
        )
    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")

def call_llm(messages: List[BaseMessage]) -> str:
    llm = get_llm()
    
    logger.info("Messages")
    logger.info(messages)
    
    response = llm.invoke(messages)
    
    logger.info("Response")
    logger.info(response)

    #with open("./data/tmp_resp.json", 'r', encoding='utf-8') as file:
    #    response = file.read()
           
    #print(response)
    # Chat-LLM возвращает ChatMessage/AIMessage; извлекаем текст
    if isinstance(response, str):
        return response
    if hasattr(response, "content"):
        return response.content
    return str(response)