from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..domain.models import Group, User
from ..infrastructure.constants import DEFAULT_GROUP_ID
from ..infrastructure.database import get_db
from ..infrastructure.repositories import (
    SQLAlchemyGroupRepository,
    SQLAlchemyUserRepository,
)
from ..infrastructure.security import get_current_user
from .schemas import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    """Create a new user.

    Persists the user using SQLAlchemy.
    """
    repo = SQLAlchemyUserRepository(db)
    try:
        repo.add(User(email=user.email, name=user.name))
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already exists")
    created = repo.get_by_email(user.email)
    assert created is not None
    # Add new user to default group (if exists)
    try:
        SQLAlchemyGroupRepository(db).add_member(DEFAULT_GROUP_ID, created.id)
    except Exception:
        # Best-effort; ignore if default group is missing
        pass
    return UserRead(id=created.id, email=created.email, name=created.name)


@router.get("/{user_id}/groups", response_model=list[Group])
def list_user_groups(user_id: str, db: Session = Depends(get_db)) -> list[Group]:
    """List groups a user belongs to."""
    try:
        uid = UUID(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    group_repo = SQLAlchemyGroupRepository(db)
    return list(group_repo.list_for_user(uid))


@router.get("/", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db)) -> list[UserRead]:
    repo = SQLAlchemyUserRepository(db)
    return [UserRead(id=u.id, email=u.email, name=u.name) for u in repo.list_all()]


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: str, db: Session = Depends(get_db)) -> UserRead:
    try:
        uid = UUID(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    repo = SQLAlchemyUserRepository(db)
    user = repo.get(uid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead(id=user.id, email=user.email, name=user.name)


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: str,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> UserRead:
    try:
        uid = UUID(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    if str(uid) != str(current.id):
        raise HTTPException(status_code=403, detail="Forbidden")
    # Fetch ORM row
    from ..infrastructure.orm import UserORM

    row = db.get(UserORM, uid)
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    # Apply updates
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
    return UserRead(id=row.id, email=row.email, name=row.name)
