"""User routes: create, list, retrieve, and update users."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.exceptions import UserExistsError, UserNotFoundError
from ..domain.models import User
from ..infrastructure.constants import DEFAULT_GROUP_ID
from ..infrastructure.database import get_db
from ..infrastructure.dependencies import get_group_repo, get_user_repo
from ..infrastructure.orm import UserORM
from ..infrastructure.repositories import (
    SQLAlchemyGroupRepository,
    SQLAlchemyUserRepository,
)
from ..infrastructure.security import get_current_user
from .schemas import GroupRead, UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead)
async def create_user(
    user: UserCreate,
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repo),
) -> UserRead:
    """Create a new user.

    Persists the user using SQLAlchemy.
    """
    try:
        user_created = await user_repo.add(User(email=user.email, name=user.name))
    except UserExistsError as exc:
        raise HTTPException(status_code=409, detail="Email already exists") from exc

    return UserRead(id=user_created.id, email=user_created.email, name=user_created.name)


@router.get("/{user_id}/groups", response_model=list[GroupRead])
async def list_user_groups(
    user_id: UUID,
    group_repo: SQLAlchemyGroupRepository = Depends(get_group_repo),
) -> list[GroupRead]:
    """List groups a user belongs to."""
    groups = await group_repo.list_for_user(user_id)
    return [GroupRead(id=g.id, name=g.name, members=g.members) for g in groups]


@router.get("/", response_model=list[UserRead])
async def list_users(
    repo: SQLAlchemyUserRepository = Depends(get_user_repo),
) -> list[UserRead]:
    """Return all users."""
    return await repo.list_all()


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: UUID,
    repo: SQLAlchemyUserRepository = Depends(get_user_repo),
) -> UserRead:
    """Return a single user by UUID."""
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: UUID,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
) -> UserRead:
    """Update the authenticated user's own profile."""
    if user_id != current.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    row = await db.get(UserORM, user_id)
    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.email is not None:
        row.email = payload.email
    if payload.name is not None:
        row.name = payload.name

    try:
        await db.commit()
        await db.refresh(row)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Email already exists")

    return row
