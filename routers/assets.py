from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from uuid import UUID
import crud
import models

router = APIRouter(
    prefix="/assets",
    tags=["assets"], # Group endpoints in Swagger UI
    responses={404: {"description": "Not found"}},
)

@router.get("", response_model=List[models.Asset])
async def read_assets(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    """Retrieves assets with pagination."""
    skip = (page - 1) * page_size
    return await crud.get_all_assets(skip=skip, limit=page_size)

@router.post("", response_model=models.Asset, status_code=201)
async def create_asset(asset: models.Asset):
    """Creates a new asset and links it to a contact."""
    # 1. Check if the contact exists
    contact = await crud.get_contact_by_uuid(asset.contact_uuid)
    if contact is None:
        raise HTTPException(status_code=400, detail=f"Contact with UUID {asset.contact_uuid} not found")

    # 2. Create the asset in the assets collection
    created_asset = await crud.create_new_asset(asset)

    # 3. Add the asset reference to the contact's list
    await crud.add_asset_to_contact(asset.contact_uuid, created_asset)

    return created_asset

@router.get("/{asset_uuid}", response_model=models.Asset)
async def read_asset(asset_uuid: UUID):
    """Retrieves a single asset by UUID."""
    db_asset = await crud.get_asset_by_uuid(asset_uuid)
    if db_asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return db_asset

@router.put("/{asset_uuid}", response_model=models.Asset)
async def update_asset(asset_uuid: UUID, asset_update: models.AssetUpdate):
    """Updates an existing asset."""
    # Check if the target asset exists first
    existing_asset = await crud.get_asset_by_uuid(asset_uuid)
    if existing_asset is None:
         raise HTTPException(status_code=404, detail="Asset not found")

    # Check if the *new* contact_uuid exists
    contact = await crud.get_contact_by_uuid(asset_update.contact_uuid)
    if contact is None:
        raise HTTPException(status_code=400, detail=f"Contact with UUID {asset_update.contact_uuid} not found for update")

    # Perform the update in the assets collection
    updated_asset = await crud.update_existing_asset(asset_uuid, asset_update)
    if updated_asset is None:
         # This case might happen if the asset was deleted between the check and update,
         # or if update_one somehow fails despite the initial check.
         raise HTTPException(status_code=404, detail="Asset not found during update")

    # --- Handle potential contact change ---
    # If the contact_uuid changed, we need to update the old and new contacts
    if existing_asset.contact_uuid != updated_asset.contact_uuid:
        # Remove from old contact's asset list
        await crud.remove_asset_from_contact(existing_asset.contact_uuid, asset_uuid)
        # Add to new contact's asset list (using the updated asset data)
        await crud.add_asset_to_contact(updated_asset.contact_uuid, updated_asset)
    else:
         # If contact didn't change, update the asset within the contact's list
         # This is more complex as it requires finding and replacing the specific asset dict
         # A simpler approach (used here) relies on the asset data being primarily in the assets collection.
         # If you *need* the contact's embedded list to be perfectly in sync *immediately* after PUT,
         # you might need a more complex update operation on the contacts collection.
         pass # Assuming the primary source is the assets collection

    return updated_asset


@router.delete("/{asset_uuid}", status_code=204) # 204 No Content is standard for DELETE
async def delete_asset(asset_uuid: UUID):
    """Deletes an asset and removes it from its contact."""
    # 1. Find the asset to get its contact_uuid
    asset_to_delete = await crud.get_asset_by_uuid(asset_uuid)
    if asset_to_delete is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    # 2. Remove the asset reference from the contact
    if asset_to_delete.contact_uuid: # Check if it has a contact linked
         await crud.remove_asset_from_contact(asset_to_delete.contact_uuid, asset_uuid)

    # 3. Delete the asset from the assets collection
    deleted = await crud.delete_asset_by_uuid(asset_uuid)
    if not deleted:
         raise HTTPException(status_code=404, detail="Asset not found during deletion")

    return None
