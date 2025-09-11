import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.infrastructure import database as dbmod
from app.infrastructure.orm import Base
from app.main import app


@pytest.fixture(scope="session")
def test_engine():
    # Force an in-memory SQLite URL for tests, regardless of external env
    os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
    engine = create_engine(
        os.environ["DATABASE_URL"],
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture()
def db_session(test_engine):
    TestingSessionLocal = sessionmaker(
        bind=test_engine, autoflush=False, autocommit=False
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session, monkeypatch):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    # Patch engine and SessionLocal used by the app
    monkeypatch.setattr(dbmod, "engine", db_session.get_bind())
    monkeypatch.setattr(dbmod, "SessionLocal", lambda: db_session)

    # Also ensure startup uses the test engine
    import app.main as mainmod

    monkeypatch.setattr(mainmod, "engine", db_session.get_bind())

    app.dependency_overrides[dbmod.get_db] = override_get_db

    with TestClient(app) as c:
        yield c
