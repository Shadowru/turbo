# BFT Semantic Analyzer (MVP)

Платформа для семантического анализа бизнес-функциональных требований (БФТ) с использованием RAG-подхода и локальных/облачных LLM. Система автоматически формирует:

- Solution Architecture-анализ БФТ
- Список задействованных/новых систем
- UML-диаграммы взаимодействий (Mermaid)
- Перечень существующих/новых интеграционных топиков

---

## ✨ Основные возможности

- **RAG по корпоративному каталогу**: ChromaDB + SQLite как реестр систем.
- **LLM-оркестрация**: поддержка Ollama (локально) и OpenAI API.
- **Автоматический вывод**: структурированный JSON + Mermaid-диаграммы (sequence, flowchart).
- **API-ориентированность**: FastAPI с REST endpoint.
- **Расширяемость**: модульная архитектура, подготовлена к интеграции UI.

---

## 🧱 Архитектура (High Level)

```mermaid
flowchart LR
    subgraph API Layer
        FastAPI
    end

    subgraph Core
        Orchestrator
        Pipeline
        Outputs
    end

    subgraph Storage
        SQLite[(SQLite)]
        Chroma[(ChromaDB)]
    end

    subgraph LLM
        Ollama[(Ollama Model)]
        OpenAI[(OpenAI API)]
    end

    FastAPI --> Orchestrator
    Orchestrator --> Pipeline
    Pipeline --> Outputs
    Orchestrator --> SQLite
    Orchestrator --> Chroma
    Pipeline --> LLM
    LLM --> Pipeline

## 🔁 Поток обработки запроса

```mermaid
sequenceDiagram
    participant User as Архитектор
    participant API as FastAPI
    participant Orchestrator
    participant Preproc
    participant RAG as ChromaDB
    participant LLM
    participant Outputs

    User->>API: POST /api/v1/analyze (BFT)
    API->>Orchestrator: process_bft()
    Orchestrator->>Preproc: clean + chunk
    Preproc->>RAG: upsertChunks()
    Orchestrator->>RAG: retrieve(top-k)
    Orchestrator->>LLM: run_architecture_chain()
    LLM-->>Orchestrator: JSON-ответ
    Orchestrator->>Outputs: build_outputs()
    Outputs-->>Orchestrator: Mermaid диаграммы
    Orchestrator-->>API: structured answer
    API-->>User: JSON + UML (Mermaid)

