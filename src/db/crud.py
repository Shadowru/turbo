from collections.abc import Sequence
from sqlmodel import select
from src.db.base import get_session
from src.db.models import System

def get_system_by_id(system_id: str) -> System | None:
    with get_session() as session:
        stmt = select(System).where(System.system_id == system_id)
        return session.exec(stmt).first()

def search_systems_by_keyword(keyword: str, limit: int = 10) -> Sequence[System]:
    pattern = f"%{keyword.lower()}%"
    with get_session() as session:
        stmt = select(System).where(System.name.ilike(pattern))
        return session.exec(stmt).fetchmany(limit)