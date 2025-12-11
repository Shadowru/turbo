from collections.abc import Sequence
from sqlalchemy.orm import selectinload
from datetime import datetime
from collections.abc import Sequence
from sqlmodel import select
from src.db.base import get_session
from src.db.models import System, BftAnalysisHistory

def get_system_by_id(system_id: str) -> System | None:
    with get_session() as session:
        stmt = select(System).where(System.system_id == system_id)
        return session.exec(stmt).first()

def search_systems_by_keyword(keyword: str, limit: int = 10) -> Sequence[System]:
    pattern = f"%{keyword.lower()}%"
    with get_session() as session:
        stmt = select(System).where(System.name.ilike(pattern))
        return session.exec(stmt).fetchmany(limit)

def list_systems_full() -> Sequence[System]:
    with get_session() as session:
        stmt = (
            select(System)
            .options(
                selectinload(System.interfaces),
                selectinload(System.topics),
            )
        )
        return session.exec(stmt).all()
    
def create_history_entry(
    bft_id: str,
    request_text: str,
    structured_output: dict,
    artifacts: dict,
    raw_llm_output: str | None,
    retrieved_context: str | None,
) -> BftAnalysisHistory:
    entry = BftAnalysisHistory(
        bft_id=bft_id,
        request_text=request_text,
        structured_output=structured_output,
        artifacts=artifacts,
        raw_llm_output=raw_llm_output,
        retrieved_context=retrieved_context,
    )
    with get_session() as session:
        session.add(entry)
        session.commit()
        session.refresh(entry)
        return entry

def list_history(
    limit: int = 20,
    bft_id: str | None = None,
) -> Sequence[BftAnalysisHistory]:
    with get_session() as session:
        stmt = select(BftAnalysisHistory).order_by(BftAnalysisHistory.created_at.desc())
        if bft_id:
            stmt = stmt.where(BftAnalysisHistory.bft_id == bft_id)
        stmt = stmt.limit(limit)
        return session.exec(stmt).all()

def get_history_by_id(history_id: int) -> BftAnalysisHistory | None:
    with get_session() as session:
        return session.get(BftAnalysisHistory, history_id)

def get_latest_history(bft_id: str | None = None) -> BftAnalysisHistory | None:
    with get_session() as session:
        stmt = select(BftAnalysisHistory).order_by(BftAnalysisHistory.created_at.desc())
        if bft_id:
            stmt = stmt.where(BftAnalysisHistory.bft_id == bft_id)
        stmt = stmt.limit(1)
        return session.exec(stmt).first()    
    