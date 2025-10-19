from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..domain.models import Group, User
from ..infrastructure.constants import DEFAULT_GROUP_ID
from ..infrastructure.database import get_db
from ..infrastructure.orm import UserORM
from ..infrastructure.repositories import (
    SQLAlchemyGroupRepository,
    SQLAlchemyUserRepository,
)
from ..infrastructure.security import get_current_user
from .schemas import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    """Create a new user and persist it using SQLAlchemy."""
    repo = SQLAlchemyUserRepository(db)
    domain_user = User(email=user.email, name=user.name)
    try:
        # The user object is mutated by SQLAlchemy and will have the ID after commit.
        repo.add(domain_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already exists")

    # The original code re-fetched the user, which is inefficient.
    # The 'domain_user' object is now populated with the ID from the database.

    # Add new user to default group (best-effort)
    try:
        SQLAlchemyGroupRepository(db).add_member(DEFAULT_GROUP_ID, domain_user.id)
    except Exception:
        # Swallowing exceptions is dangerous and should be avoided.
        # At a minimum, this failure should be logged.
        pass

    return UserRead.from_orm(domain_user)


@router.get("/{user_id}/groups", response_model=list[Group])
def list_user_groups(user_id: UUID, db: Session = Depends(get_db)) -> list[Group]:
    """List groups a user belongs to."""
    # By using `user_id: UUID`, FastAPI handles UUID validation automatically,
    # returning a 422 Unprocessable Entity response for invalid UUIDs.
    group_repo = SQLAlchemyGroupRepository(db)
    return list(group_repo.list_for_user(user_id))


@router.get("/", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db)) -> list[UserRead]:
    repo = SQLAlchemyUserRepository(db)
    users = repo.list_all()
    return [UserRead.from_orm(u) for u in users]


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: UUID, db: Session = Depends(get_db)) -> UserRead:
    # Using `user_id: UUID` for automatic validation.
    repo = SQLAlchemyUserRepository(db)
    user = repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead.from_orm(user)


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: UUID,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> UserRead:
    # Using `user_id: UUID` for automatic validation.
    if user_id != current.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Note: Bypassing the repository to fetch/update the UserORM object directly
    # is a leak in the abstraction layer. The UserRepository should have an
    # `update` method that encapsulates this logic.
    row = db.get(UserORM, user_id)
    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    # Use Pydantic's `model_dump` to get a dict of only the fields that were set.
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(row, key, value)

    try:
        db.add(row)
        db.commit()
        db.refresh(row)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already exists")

    return UserRead.from_orm(row)
