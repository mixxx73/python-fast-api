from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, condecimal, constr


# Users
class UserCreate(BaseModel):
    email: EmailStr
    name: constr(min_length=1, max_length=255)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[constr(min_length=1, max_length=255)] = None


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    name: str


# Groups
class GroupCreate(BaseModel):
    name: constr(min_length=1, max_length=255)


class GroupRead(BaseModel):
    id: UUID
    name: str
    members: list[UUID] = Field(default_factory=list)


class GroupUpdate(BaseModel):
    name: constr(min_length=1, max_length=255)


# Expenses
class ExpenseCreate(BaseModel):
    group_id: UUID
    payer_id: UUID
    amount: condecimal(gt=0)
    description: Optional[constr(max_length=1024)] = None


class ExpenseRead(BaseModel):
    id: UUID
    group_id: UUID
    payer_id: UUID
    amount: float
    created_at: datetime
    description: Optional[str] = None


# Balances
class BalanceEntry(BaseModel):
    user_id: UUID
    balance: float
