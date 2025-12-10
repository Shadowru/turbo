from contextlib import contextmanager
from sqlmodel import SQLModel, create_engine, Session
from src.config import get_settings

settings = get_settings()
engine = create_engine(
    f"sqlite:///{settings.sqlite_path}",
    echo=False,
    connect_args={"check_same_thread": False},
)

def init_db() -> None:
    SQLModel.metadata.create_all(engine)

@contextmanager
def get_session() -> Session:
    with Session(engine) as session:
        yield session