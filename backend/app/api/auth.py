import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from ..domain.exceptions import UserExistsError
from ..domain.models import User
from ..infrastructure.constants import DEFAULT_GROUP_ID
from ..infrastructure.database import get_db
from ..infrastructure.dependencies import get_user_service
from ..infrastructure.orm import UserORM
from ..infrastructure.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SignupRequest(BaseModel):
    email: EmailStr
    name: str
    password: str
    is_admin: bool = False


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/signup", response_model=Token)
def signup(
    payload: SignupRequest,
    user_service=Depends(get_user_service),
) -> Token:
    pw_hash = hash_password(payload.password)
    user = User(
        email=payload.email,
        name=payload.name,
        is_admin=payload.is_admin,
        password_hash=pw_hash,
    )

    try:
        user_created = user_service(user, DEFAULT_GROUP_ID)
    except UserExistsError as exc:
        raise HTTPException(status_code=409, detail="Email already exists") from exc

    token = create_access_token(str(user_created.id))

    return Token(access_token=token)


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:

    row = db.query(UserORM).filter(UserORM.email == payload.email).first()
    if (
        not row
        or not row.password_hash
        or not verify_password(payload.password, row.password_hash)
    ):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(str(row.id))

    return Token(access_token=token)


@router.get("/me", response_model=User)
def read_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
