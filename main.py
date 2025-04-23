from typing import List, Optional
from uuid import UUID, uuid4
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime
import motor.motor_asyncio
from bson import ObjectId
from pydantic import BaseConfig
from enum import Enum
from bson import ObjectId, Binary
from bson.codec_options import CodecOptions, UuidRepresentation
app = FastAPI()

MONGODB_URL = "mongodb://localhost:27017"
MONGODB_DB_NAME = "contacts_assets_db"
MONGODB_CONTACTS_COLLECTION = "contacts"
MONGODB_ASSETS_COLLECTION = "assets"

client = motor.motor_asyncio.AsyncIOMotorClient(
    MONGODB_URL,
    uuidRepresentation='standard'
)

db = client[MONGODB_DB_NAME]
contacts_collection = db[MONGODB_CONTACTS_COLLECTION]
assets_collection = db[MONGODB_ASSETS_COLLECTION]


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
        arbitrary_types_allowed = True  # Allow UUID


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
        arbitrary_types_allowed = True # Allow UUID


async def get_contact_by_uuid(contact_uuid: UUID) -> Optional[Contact]:
    """
    Retrieves a contact from the database by UUID.
    """
    contact_data = await contacts_collection.find_one({"uuid": contact_uuid})
    if contact_data:
        return Contact(**contact_data)
    return None


async def get_asset_by_uuid(asset_uuid: UUID) -> Optional[Asset]:
    """
    Retrieves an asset from the database by UUID.
    """
    asset_data = await assets_collection.find_one({"uuid": asset_uuid})
    if asset_data:
        return Asset(**asset_data)
    return None

@app.get("/contacts")
async def get_contacts() -> List[Contact]:
    """
    Retrieves all contacts from the database.
    """
    contacts_data = await contacts_collection.find().to_list(None)
    return [Contact(**contact) for contact in contacts_data]



@app.get("/contacts/{contact_uuid}")
async def get_contact(contact_uuid: UUID) -> Contact:
    """
    Retrieves a single contact by UUID.

    Args:
        contact_uuid (UUID): The UUID of the contact to retrieve.

    Returns:
        Contact: The contact with the given UUID.

    Raises:
        HTTPException: 404 if the contact is not found.
    """
    contact = await get_contact_by_uuid(contact_uuid)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact



@app.post("/contacts")
async def create_contact(contact: Contact) -> Contact:
    """
    Creates a new contact in the database.

    Args:
        contact (Contact): The contact to create.

    Returns:
        Contact: The created contact.
    """
    contact_data = contact.dict()
    await contacts_collection.insert_one(contact_data)
    return contact


@app.get("/assets")
async def get_assets(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
) -> List[Asset]:
    """
    Retrieves all assets from the database with pagination.

    Args:
        page (int, optional): The page number to retrieve. Defaults to 1.
        page_size (int, optional): The number of items per page. Defaults to 10.

    Returns:
        List[Asset]: The list of assets for the given page.
    """
    skip = (page - 1) * page_size
    assets_data = await assets_collection.find().skip(skip).limit(page_size).to_list(None)
    return [Asset(**asset) for asset in assets_data]



@app.get("/assets/{asset_uuid}")
async def get_asset(asset_uuid: UUID) -> Asset:
    """
    Retrieves a single asset by UUID.

    Args:
        asset_uuid (UUID): The UUID of the asset to retrieve.

    Returns:
        Asset: The asset with the given UUID.

    Raises:
        HTTPException: 404 if the asset is not found.
    """
    asset = await get_asset_by_uuid(asset_uuid)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset



@app.post("/assets")
async def create_asset(asset: Asset) -> Asset:
    """
    Creates a new asset in the database.

    Args:
        asset (Asset): The asset to create.

    Returns:
        Asset: The created asset.
    """
    contact = await get_contact_by_uuid(asset.contact_uuid)
    if contact is None:
        raise HTTPException(status_code=400, detail="Contact not found for this asset")
    asset_data = asset.dict()
    await assets_collection.insert_one(asset_data)
    await contacts_collection.update_one(
        {"uuid": asset.contact_uuid},
        {"$push": {"assets": asset.dict()}}  # Store the asset as a dictionary
    )

    return asset



@app.put("/assets/{asset_uuid}")
async def update_asset(asset_uuid: UUID, updated_asset: Asset) -> Asset:
    """
    Updates an existing asset in the database.

    Args:
        asset_uuid (UUID): The UUID of the asset to update.
        updated_asset (Asset): The updated asset data.

    Returns:
        Asset: The updated asset.

    Raises:
        HTTPException: 404 if the asset is not found.
        HTTPException: 400 if the contact_uuid in the updated_asset doesn't exist.
    """
    asset = await get_asset_by_uuid(asset_uuid)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    contact = await get_contact_by_uuid(updated_asset.contact_uuid)
    if contact is None:
        raise HTTPException(status_code=400, detail="Contact not found for this asset")

    asset_data = updated_asset.dict(exclude={"uuid", "created_at"})
    asset_data["updated_at"] = datetime.utcnow()
    result = await assets_collection.update_one(
        {"uuid": asset_uuid},
        {"$set": asset_data}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Asset not found")
    return await get_asset_by_uuid(asset_uuid)


@app.delete("/assets/{asset_uuid}")
async def delete_asset(asset_uuid: UUID):
    """
    Deletes an asset by UUID from the database.  Also removes it from the owning contact.

    Args:
        asset_uuid (UUID): The UUID of the asset to delete.

    Raises:
        HTTPException: 404 if the asset is not found.
    """
    asset = await get_asset_by_uuid(asset_uuid)
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    contact = await get_contact_by_uuid(asset.contact_uuid)
    if contact:
        await contacts_collection.update_one(
            {"uuid": contact.uuid},
            {"$pull": {"assets": {"uuid": asset_uuid}}}
        )
    result = await assets_collection.delete_one({"uuid": asset_uuid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Asset not found")
    return {"detail": "Asset deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
