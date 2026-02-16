"""Domain models representing the core business entities."""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class User(BaseModel):
    """Domain model representing an application user."""

    id: UUID = Field(default_factory=uuid4)
    email: str
    name: str
    is_admin: bool = False
    password_hash: Optional[str] = None


class Group(BaseModel):
    """Domain model representing a group of users sharing expenses."""

    id: UUID = Field(default_factory=uuid4)
    name: str
    members: List[UUID] = Field(default_factory=list)
    # created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Expense(BaseModel):
    """Domain model representing an expense paid by one member on behalf of a group."""

    id: UUID = Field(default_factory=uuid4)
    group_id: UUID
    payer_id: UUID
    amount: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: Optional[str] = None
