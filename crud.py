from typing import List, Optional
from uuid import UUID
from datetime import datetime

import models
from database import contacts_collection, assets_collection


async def get_contact_by_uuid(contact_uuid: UUID) -> Optional[models.Contact]:
    """Retrieves a contact from the database by UUID."""
    contact_data = await contacts_collection.find_one({"uuid": contact_uuid})
    if contact_data:
        if 'assets' in contact_data and isinstance(contact_data['assets'], list):
             contact_data['assets'] = [models.Asset(**asset_data) for asset_data in contact_data['assets']]
        return models.Contact(**contact_data)
    return None

async def get_all_contacts() -> List[models.Contact]:
    """Retrieves all contacts from the database."""
    contacts_data = await contacts_collection.find().to_list(None)
    parsed_contacts = []
    for contact in contacts_data:
         if 'assets' in contact and isinstance(contact['assets'], list):
             contact['assets'] = [models.Asset(**asset_data) for asset_data in contact['assets']]
         parsed_contacts.append(models.Contact(**contact))
    return parsed_contacts


async def create_new_contact(contact: models.Contact) -> models.Contact:
    """Creates a new contact in the database."""
    contact_data = contact.dict()
    await contacts_collection.insert_one(contact_data)
    return contact # Return the original Pydantic model

async def add_asset_to_contact(contact_uuid: UUID, asset: models.Asset):
    """Adds an asset (as dict) to a contact's asset list."""
    await contacts_collection.update_one(
        {"uuid": contact_uuid},
        {"$push": {"assets": asset.dict()}}
    )

async def remove_asset_from_contact(contact_uuid: UUID, asset_uuid: UUID):
     """Removes an asset from a contact's asset list by asset UUID."""
     await contacts_collection.update_one(
         {"uuid": contact_uuid},
         {"$pull": {"assets": {"uuid": asset_uuid}}}
     )

async def get_asset_by_uuid(asset_uuid: UUID) -> Optional[models.Asset]:
    """Retrieves an asset from the database by UUID."""
    asset_data = await assets_collection.find_one({"uuid": asset_uuid})
    if asset_data:
        return models.Asset(**asset_data)
    return None

async def get_all_assets(skip: int = 0, limit: int = 100) -> List[models.Asset]:
    """Retrieves assets from the database with pagination."""
    assets_data = await assets_collection.find().skip(skip).limit(limit).to_list(None)
    return [models.Asset(**asset) for asset in assets_data]

async def create_new_asset(asset: models.Asset) -> models.Asset:
    """Creates a new asset in the database."""
    asset_data = asset.dict()
    await assets_collection.insert_one(asset_data)
    return asset

async def update_existing_asset(asset_uuid: UUID, asset_update: models.AssetUpdate) -> Optional[models.Asset]:
    """Updates an existing asset in the database."""
    update_data = asset_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    result = await assets_collection.update_one(
        {"uuid": asset_uuid},
        {"$set": update_data}
    )
    if result.modified_count == 1:
        return await get_asset_by_uuid(asset_uuid)
    return None

async def delete_asset_by_uuid(asset_uuid: UUID) -> bool:
    """Deletes an asset by UUID from the database."""
    result = await assets_collection.delete_one({"uuid": asset_uuid})
    return result.deleted_count == 1
