from langchain.prompts import ChatPromptTemplate
from langchain.schema import AIMessage, HumanMessage
from src.llm.client import call_llm

SOLUTION_SCHEMA = """
{
  "architecture_analysis": {...},
  "involved_systems": [...],
  "uml_diagrams": [...],
  "integration_topics": [...]
}
"""

def run_architecture_chain(bft_text: str, context: str) -> str:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Ты — корпоративный архитектор. Отвечай строго в JSON без лишнего текста."),
        ("human", "БФТ:\n{bft}\n\nКонтекст:\n{context}\n\nСледуй схеме:\n" + SOLUTION_SCHEMA),
    ])
    messages = prompt.format_messages(bft=bft_text, context=context)
    return call_llm(messages)