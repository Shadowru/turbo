from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

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