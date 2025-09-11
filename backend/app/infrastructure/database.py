import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .secrets import get_secret


def _database_url() -> str:
    # 1) Full URL from secrets/env
    url = get_secret("DATABASE_URL")
    if url:
        return url
    # 2) Assemble from parts, with password from secrets
    dialect = os.getenv("DB_DIALECT", "postgresql+psycopg2")
    user = os.getenv("DB_USER", "app")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "app")
    password = get_secret("DB_PASSWORD", os.getenv("DB_PASSWORD", "")) or ""
    auth = f"{user}:{password}@" if password else f"{user}@"
    return f"{dialect}://{auth}{host}:{port}/{name}"


DATABASE_URL = _database_url()

engine = create_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator:
    """FastAPI dependency that yields a SQLAlchemy session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
