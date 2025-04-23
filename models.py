from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime
from enum import Enum

class AssetCategory(str, Enum):
    EQUITY = "EQUITY"
    FIXED_INCOME = "FIXED_INCOME"
    REAL_ESTATE = "REAL_ESTATE"
    CRYPTO = "CRYPTO"

class Asset(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    contact_uuid: UUID
    name: str = Field(..., min_length=1, max_length=200)
    value: float = Field(..., gt=0)
    active: bool = Field(default=True)
    category: AssetCategory
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    @validator('name')
    def validate_name(cls, value):
        if not value.strip():
            raise ValueError("Name cannot be empty or contain only spaces")
        return value.strip()

    @validator('value')
    def validate_value(cls, value):
        if value <= 0:
            raise ValueError("Value must be greater than zero")
        return value

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            UUID: lambda u: str(u)
        }


class Contact(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    assets: List[Asset] = Field(default_factory=list)

    @validator('first_name')
    def validate_first_name(cls, value):
        if not value.strip():
            raise ValueError("First name cannot be empty or contain only spaces")
        return value.strip()

    @validator('last_name')
    def validate_last_name(cls, value):
        if not value.strip():
            raise ValueError("Last name cannot be empty or contain only spaces")
        return value.strip()

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            UUID: lambda u: str(u)
        }

# Optional: Define update models if you want different fields for PUT requests
class AssetUpdate(BaseModel):
    contact_uuid: UUID
    name: str = Field(..., min_length=1, max_length=200)
    value: float = Field(..., gt=0)
    active: bool = Field(default=True)
    category: AssetCategory
    # Exclude fields not updatable via PUT like uuid, created_at

    @validator('name')
    def validate_name(cls, value):
        if not value.strip():
            raise ValueError("Name cannot be empty or contain only spaces")
        return value.strip()

    @validator('value')
    def validate_value(cls, value):
        if value <= 0:
            raise ValueError("Value must be greater than zero")
        return value

    class Config:
         arbitrary_types_allowed = True
         json_encoders = {
             UUID: lambda u: str(u)
         }
