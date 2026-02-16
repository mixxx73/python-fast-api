"""Database engine and session factory configuration."""

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .secrets import get_secret


def _database_url() -> str:
    """Build the database URL from secrets or individual env vars."""
    # 1) Full URL from secrets/env
    url = get_secret("DATABASE_URL")

    if url:
        return url

    dialect = os.getenv("DB_DIALECT", "postgresql+asyncpg")
    user = os.getenv("DB_USER", "app")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "app")
    password = get_secret("DB_PASSWORD", os.getenv("DB_PASSWORD", "")) or ""
    auth = f"{user}:{password}@" if password else f"{user}@"

    return f"{dialect}://{auth}{host}:{port}/{name}"


DATABASE_URL = _database_url()

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    pool_pre_ping=True,
)

async_session_maker = async_sessionmaker(
    engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async SQLAlchemy session."""
    async with async_session_maker() as session:
        yield session
