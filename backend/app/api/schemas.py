from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, condecimal, constr, field_validator


# Base configuration for schemas that map from ORM models
class BaseOrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


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
    is_admin: bool = False


class GroupBase(BaseModel):
    name: constr(min_length=1, max_length=255)


class GroupCreate(GroupBase):
    pass


class GroupUpdate(GroupBase):
    pass


class GroupRead(GroupBase, BaseOrmModel):
    id: UUID
    members: list[UUID] = Field(default_factory=list)


class ExpenseBase(BaseModel):
    group_id: UUID
    payer_id: UUID
    amount: condecimal(gt=Decimal("0"))
    description: Optional[constr(max_length=1024)] = None


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseRead(ExpenseBase, BaseOrmModel):
    id: UUID
    amount: float = Field(...)

    @field_validator("amount", mode="before")
    @classmethod
    def convert_cents_to_dollars(cls, v: int | float) -> float:
        if isinstance(v, (int, float)):
            if isinstance(v, float) and not v.is_integer():
                return v
            return float(v) / 100.0
        return float(v)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class BalanceEntry(BaseOrmModel):
    user_id: UUID
    balance: float = Field(...)
    @field_validator("balance", mode="before")
    @classmethod
    def convert_cents_to_dollars(cls, v: int | float) -> float:
        if isinstance(v, (int, float)):
            if isinstance(v, float) and not v.is_integer():
                return v
            return float(v) / 100.0
        return float(v)
    model_config = ConfigDict(from_attributes=True)
