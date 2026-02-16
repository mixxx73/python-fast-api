"""Password hashing, JWT creation/decoding, and FastAPI auth dependency."""

import asyncio
import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID as UUID_t

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.models import User
from .database import get_db
from .orm import UserORM
from .secrets import get_secret

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=True)

SECRET_KEY = get_secret("SECRET_KEY", "dev-insecure-secret")
if not SECRET_KEY or len(SECRET_KEY) < 16:
    SECRET_KEY = "dev-insecure-secret"
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


async def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt (runs in executor to stay async)."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, pwd_context.hash, password)


async def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, pwd_context.verify, plain_password, password_hash
    )


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT with the given subject and optional expiry."""
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    now = datetime.now(tz=timezone.utc)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_token(token: str) -> dict:
    """Decode and validate a JWT, raising HTTP 401 on failure."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """FastAPI dependency: extract and validate bearer token, return the user."""
    token = credentials.credentials
    payload = decode_token(token)
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Invalid token subject")
    try:
        uid = UUID_t(str(sub))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token subject")
    row = await db.get(UserORM, uid)
    if not row:
        raise HTTPException(status_code=401, detail="User not found")
    return User(id=row.id, email=row.email, name=row.name, is_admin=row.is_admin)
