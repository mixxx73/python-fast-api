"""Pydantic request/response schemas for the API layer."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    condecimal,
    constr,
    field_validator,
)


# Base configuration for schemas that map from ORM models
class BaseOrmModel(BaseModel):
    """Base schema with ORM mode enabled for all read schemas."""

    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    """Shared user fields used by create and read schemas."""

    email: EmailStr
    name: constr(min_length=1, max_length=255)


class UserCreate(UserBase):
    """Schema for creating a new user."""


class UserUpdate(BaseModel):
    """Schema for partially updating a user (all fields optional)."""

    # All fields are optional for PATCH operations
    email: Optional[EmailStr] = None
    name: Optional[constr(min_length=1, max_length=255)] = None


class UserRead(UserBase, BaseOrmModel):
    """Schema for returning user data in responses."""

    id: UUID
    is_admin: bool = False

    model_config = ConfigDict(from_attributes=True)


class GroupBase(BaseModel):
    """Shared group fields."""

    name: constr(min_length=1, max_length=255)


class GroupCreate(GroupBase):
    """Schema for creating a new group."""


class GroupUpdate(GroupBase):
    """Schema for updating a group name."""


class GroupRead(GroupBase, BaseOrmModel):
    """Schema for returning group data in responses."""

    id: UUID
    members: list[UUID] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ExpenseBase(BaseModel):
    """Shared expense fields."""

    group_id: UUID
    payer_id: UUID
    amount: condecimal(gt=Decimal("0"))
    description: Optional[constr(max_length=1024)] = None


class ExpenseCreate(ExpenseBase):
    """Schema for creating a new expense."""


class ExpenseRead(ExpenseBase, BaseOrmModel):
    """Schema for returning expense data; converts stored cents to dollars."""

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
    """Schema for a single user's balance within a group."""

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
