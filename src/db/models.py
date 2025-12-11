from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from sqlalchemy import Column, JSON

class System(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    system_id: str = Field(index=True, unique=True)
    name: str
    description: Optional[str] = None
    domain: Optional[str] = None
    owner: Optional[str] = None

    interfaces: List["SystemInterface"] = Relationship(back_populates="system")
    topics: List["IntegrationTopic"] = Relationship(back_populates="system")

class SystemInterface(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    system_id: int = Field(foreign_key="system.id")
    interface_type: str
    endpoint: Optional[str] = None
    description: Optional[str] = None

    system: System = Relationship(back_populates="interfaces")

class IntegrationTopic(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    system_id: int = Field(foreign_key="system.id")
    name: str
    direction: str  # publisher/subscriber
    payload_schema: Optional[str] = None
    notes: Optional[str] = None

    system: System = Relationship(back_populates="topics")
    
class BftAnalysisHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    bft_id: str = Field(index=True)
    request_text: str
    structured_output: dict = Field(sa_column=Column(JSON))
    artifacts: dict = Field(sa_column=Column(JSON))
    raw_llm_output: Optional[str] = None
    retrieved_context: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)