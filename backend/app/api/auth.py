"""Authentication routes: signup, login, and current-user lookup."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.exceptions import UserExistsError
from ..domain.models import User
from ..infrastructure.constants import DEFAULT_GROUP_ID
from ..infrastructure.database import get_db
from ..infrastructure.repositories import SQLAlchemyGroupRepository, SQLAlchemyUserRepository
from ..infrastructure.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from ..infrastructure.orm import UserORM

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


class Token(BaseModel):
    """JWT bearer token returned after successful auth."""

    access_token: str
    token_type: str = "bearer"


class SignupRequest(BaseModel):
    """Payload for user registration."""

    email: EmailStr
    name: str
    password: str
    is_admin: bool = False


class LoginRequest(BaseModel):
    """Payload for user login."""

    email: EmailStr
    password: str


@router.post("/signup", response_model=Token)
async def signup(payload: SignupRequest, db: AsyncSession = Depends(get_db)) -> Token:
    """Register a new user and return a JWT token."""
    repo = SQLAlchemyUserRepository(db)
    pw_hash = await hash_password(payload.password)
    user = User(
        email=payload.email,
        name=payload.name,
        is_admin=payload.is_admin,
        password_hash=pw_hash,
    )

    try:
        user_created = await repo.add(user)
    except UserExistsError as exc:
        raise HTTPException(status_code=409, detail="Email already exists") from exc

    try:
        await SQLAlchemyGroupRepository(db).add_member(DEFAULT_GROUP_ID, user_created.id)
    except Exception:
        logger.error(
            f"Failed to add new user to default group {DEFAULT_GROUP_ID}.",
            exc_info=True,
            extra={"group_id": str(DEFAULT_GROUP_ID)},
        )

    token = create_access_token(str(user_created.id))
    return Token(access_token=token)


@router.post("/login", response_model=Token)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> Token:
    """Authenticate with email/password and return a JWT token."""
    result = await db.execute(select(UserORM).where(UserORM.email == payload.email))
    row = result.scalar_one_or_none()
    if not row or not row.password_hash or not await verify_password(payload.password, row.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(str(row.id))
    return Token(access_token=token)


@router.get("/me", response_model=User)
async def read_me(current_user: User = Depends(get_current_user)) -> User:
    """Return the profile of the currently authenticated user."""
    return current_user
