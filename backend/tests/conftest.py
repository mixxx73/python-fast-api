import os

# MUST be set before any app imports — database.py creates the engine at module load time
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.infrastructure import database as dbmod  # noqa: E402
from app.infrastructure.orm import Base  # noqa: E402
from app.main import app  # noqa: E402

# -----------------------------------------------------------------------
# The app-level engine was created with the sqlite URL above.
# Reconfigure it to use StaticPool so all connections share one in-memory DB.
# -----------------------------------------------------------------------
_test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_test_session_factory = async_sessionmaker(
    _test_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

# Replace the app-level engine so the lifespan startup uses our test engine
dbmod.engine = _test_engine


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _create_tables():
    """Create all tables once for the entire test session."""
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture()
async def db_session() -> AsyncSession:
    async with _test_session_factory() as session:
        yield session


@pytest_asyncio.fixture()
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[dbmod.get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
