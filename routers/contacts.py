from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import UUID

import crud
import models

router = APIRouter(
    prefix="/contacts",
    tags=["contacts"], # Group endpoints in Swagger UI
    responses={404: {"description": "Not found"}},
)

@router.get("", response_model=List[models.Contact])
async def read_contacts():
    """Retrieves all contacts."""
    return await crud.get_all_contacts()

@router.post("", response_model=models.Contact, status_code=201) # Use 201 for creation
async def create_contact(contact: models.Contact):
    """Creates a new contact."""
    # Optional: Check if email already exists
    # existing_contact = await crud.get_contact_by_email(contact.email)
    # if existing_contact:
    #     raise HTTPException(status_code=400, detail="Email already registered")
    created_contact = await crud.create_new_contact(contact)
    return created_contact

@router.get("/{contact_uuid}", response_model=models.Contact)
async def read_contact(contact_uuid: UUID):
    """Retrieves a single contact by UUID."""
    db_contact = await crud.get_contact_by_uuid(contact_uuid)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

# Add PUT/DELETE endpoints for contacts if needed
