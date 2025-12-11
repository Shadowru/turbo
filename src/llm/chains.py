from textwrap import dedent
from langchain.prompts import ChatPromptTemplate
from src.llm.client import call_llm

SOLUTION_SCHEMA = dedent(
    """
    {
      "architecture_analysis": {
        "business_context": "...",
        "functional_blocks": [],
        "non_functional": {},
        "solution_options": [],
        "selected_option": null,
        "risks": [],
        "dependencies": []
      },
      "involved_systems": [
        {
          "system_id": "string",
          "role": "string",
          "existing": true,
          "confidence": 0.0,
          "notes": "string"
        }
      ],
      "uml_diagrams": [
        {
          "type": "sequence",
          "description": "string",
          "actors": [],
          "steps": [
            {"from": "string", "to": "string", "message": "string"}
          ]
        },
        {
          "type": "component",
          "systems": [
            {
              "system_id": "string",
              "label": "string",
              "existing": true,
              "integrations": [
                {"target": "string", "label": "string"}
              ]
            }
          ]
        }
      ],
      "integration_topics": [
        {
          "topic": "string",
          "status": "existing",
          "publisher": "string",
          "subscriber": ["string"],
          "payload_schema_ref": "string",
          "actions": ["string"]
        }
      ]
    }
    """
).strip()

def run_architecture_chain(bft_text: str, context: str) -> str:
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
            "Ты — корпоративный архитектор. Отвечай строго в JSON без лишнего текста. "
            "Если в секции KNOWN SYSTEMS указан system_id/name, используй их ровно в таком виде. "
            "Не придумывай новые названия для уже известных систем. "
            "Если нужна новая система, явным образом укажи её как existing=false и придумай понятное имя.",            ),
            (
                "human", 
                "БФТ:\n{bft}\n\nКонтекст (RAG):\n{context}\n\nВерни JSON по схеме:\n{schema}"
            )
        ]
    )

    messages = prompt.format_messages(
        bft=bft_text,
        context=context,
        schema=SOLUTION_SCHEMA,
    )
    return call_llm(messages)