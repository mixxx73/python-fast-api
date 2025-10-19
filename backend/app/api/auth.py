from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..domain.models import User
from ..infrastructure.constants import DEFAULT_GROUP_ID
from ..infrastructure.database import get_db
from ..infrastructure.orm import UserORM
from ..infrastructure.repositories import (
    SQLAlchemyGroupRepository,
    SQLAlchemyUserRepository,
)
from ..infrastructure.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)

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
def signup(payload: SignupRequest, db: Session = Depends(get_db)) -> Token:
    repo = SQLAlchemyUserRepository(db)
    pw_hash = hash_password(payload.password)
    user = User(email=payload.email, name=payload.name, is_admin=payload.is_admin)
    try:
        repo.add_with_password(user, pw_hash)
    except IntegrityError:
        db.rollback()
        # This is the correct way to handle unique constraints.
        # A pre-check is redundant and could lead to race conditions.
        raise HTTPException(status_code=409, detail="Email already exists")

    # Add new user to default group (best-effort)
    try:
        SQLAlchemyGroupRepository(db).add_member(DEFAULT_GROUP_ID, user.id)
    except Exception:
        # Swallowing exceptions is dangerous. If this is a non-critical
        # "best-effort" operation, the failure should at least be logged for
        # later review. For example:
        # logging.warning(f"Failed to add user {user.id} to default group")
        pass

    token = create_access_token(str(user.id))
    return Token(access_token=token)


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    # Note: Bypassing the repository to fetch the UserORM object directly
    # is a pragmatic choice to access the password hash, but it does represent
    # a leak in the abstraction layer. A cleaner solution would be to have
    # a method in the UserRepository for authentication that handles this logic.
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
