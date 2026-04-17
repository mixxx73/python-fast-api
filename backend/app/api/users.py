from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.exceptions import UserExistsError
from ..domain.models import User
from ..infrastructure.constants import DEFAULT_GROUP_ID
from ..infrastructure.database import get_db
from ..infrastructure.orm import UserORM
from ..infrastructure.repositories import SQLAlchemyGroupRepository, SQLAlchemyUserRepository
from ..infrastructure.security import get_current_user
from .schemas import GroupRead, UserCreate, UserRead, UserUpdate, PasswordChange

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)) -> UserRead:
    """Create a new user.

    Persists the user using SQLAlchemy.
    """
    repo = SQLAlchemyUserRepository(db)
    try:
        user_created = await repo.add(User(email=user.email, name=user.name))
    except UserExistsError as exc:
        raise HTTPException(status_code=409, detail="Email already exists") from exc

    try:
        await SQLAlchemyGroupRepository(db).add_member(DEFAULT_GROUP_ID, user_created.id)
    except Exception:
        pass

    return user_created


@router.get("/{user_id}/groups", response_model=list[GroupRead])
async def list_user_groups(user_id: UUID, db: AsyncSession = Depends(get_db)) -> list[GroupRead]:
    """List groups a user belongs to."""
    group_repo = SQLAlchemyGroupRepository(db)
    groups = await group_repo.list_for_user(user_id)
    return [GroupRead(id=g.id, name=g.name, members=g.members) for g in groups]


@router.get("/", response_model=list[UserRead])
async def list_users(db: AsyncSession = Depends(get_db)) -> list[UserRead]:
    repo = SQLAlchemyUserRepository(db)
    return await repo.list_all()


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)) -> UserRead:
    repo = SQLAlchemyUserRepository(db)
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


@router.post("/{user_id}/password", status_code=204)
async def change_password(
    user_id: UUID,
    payload: "PasswordChange",
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_user),
) -> None:
    """Change the authenticated user's password.

    Verifies the current password, hashes the new password, and updates the user row.
    """
    if user_id != current.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    row = await db.get(UserORM, user_id)
    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify current password
    from ..infrastructure.security import verify_password, hash_password

    if not row.password_hash:
        # No password set; disallow change without explicit flow
        raise HTTPException(status_code=403, detail="Current password incorrect")

    ok = await verify_password(payload.current_password, row.password_hash)
    if not ok:
        raise HTTPException(status_code=403, detail="Current password incorrect")

    # Hash and store new password
    row.password_hash = await hash_password(payload.new_password)
    await db.commit()
    return None
