from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, condecimal, constr


# Base configuration for schemas that map from ORM models
class BaseOrmModel(BaseModel):
    class Config:
        orm_mode = True


# Users
class UserBase(BaseModel):
    email: EmailStr
    name: constr(min_length=1, max_length=255)


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    # All fields are optional for PATCH operations
    email: Optional[EmailStr] = None
    name: Optional[constr(min_length=1, max_length=255)] = None


class UserRead(UserBase, BaseOrmModel):
    id: UUID


# Groups
class GroupBase(BaseModel):
    name: constr(min_length=1, max_length=255)


class GroupCreate(GroupBase):
    pass


class GroupUpdate(GroupBase):
    pass


class GroupRead(GroupBase, BaseOrmModel):
    id: UUID
    members: list[UUID] = Field(default_factory=list)


# Expenses
class ExpenseBase(BaseModel):
    group_id: UUID
    payer_id: UUID
    # Using Decimal for financial calculations is a best practice to avoid precision issues.
    amount: condecimal(gt=Decimal("0"))
    description: Optional[constr(max_length=1024)] = None


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseRead(ExpenseBase, BaseOrmModel):
    id: UUID
    # Note: The amount is converted to a float for the API response.
    # While common, be mindful of floating-point inaccuracies in client-side logic.
    amount: float
    created_at: datetime


# Balances
class BalanceEntry(BaseOrmModel):
    user_id: UUID
    balance: float
