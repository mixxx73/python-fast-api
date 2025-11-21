from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..domain.exceptions import UserExistsError, UserNotFoundError
from ..domain.models import User
from ..infrastructure.database import get_db
from ..infrastructure.dependencies import get_group_repo, get_user_repo
from ..infrastructure.repositories import (
    SQLAlchemyGroupRepository,
    SQLAlchemyUserRepository,
)
from ..infrastructure.security import get_current_user
from .schemas import GroupRead, UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead)
def create_user(
    user: UserCreate,
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repo),
) -> UserRead:
    """Create a new user.

    Persists the user using SQLAlchemy.
    """
    try:
        new_user = User(email=user.email, name=user.name)
        user_created = user_repo.add(new_user)
    except UserExistsError as exc:
        raise HTTPException(status_code=409, detail="Email already exists") from exc

    return user_created


@router.get("/{user_id}/groups", response_model=list[GroupRead])
def list_user_groups(
    user_id: UUID,
    group_repo: SQLAlchemyGroupRepository = Depends(get_group_repo),
) -> list[GroupRead]:
    """List groups a user belongs to."""

    return group_repo.list_for_user(user_id)


@router.get("/", response_model=list[UserRead])
def list_users(
    repo: SQLAlchemyUserRepository = Depends(get_user_repo),
) -> list[UserRead]:

    return repo.list_all()


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: UUID, repo: SQLAlchemyUserRepository = Depends(get_user_repo)
) -> UserRead:

    try:
        user = repo.get(user_id)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=404, detail="User not found") from exc

    return user


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: UUID,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> UserRead:

    if user_id != current.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    from ..infrastructure.orm import UserORM

    row = db.get(UserORM, user_id)
    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.email is not None:
        row.email = payload.email
    if payload.name is not None:
        row.name = payload.name

    try:
        db.add(row)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already exists")

    return row
