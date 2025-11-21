from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    email: str
    name: str
    is_admin: bool = False


class Group(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    members: List[UUID] = Field(default_factory=list)


class Expense(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    group_id: UUID
    payer_id: UUID
    amount: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: Optional[str] = None
