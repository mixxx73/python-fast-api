"""FastAPI application entry point: wires routers, lifespan, and tracing."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api import auth, expenses, groups, users
from .infrastructure.constants import DEFAULT_GROUP_ID, DEFAULT_GROUP_NAME
from .infrastructure.database import async_session_maker, engine
from .infrastructure.orm import Base, GroupORM
from .observability import init_tracing


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup (table creation, seeding) and shutdown."""
    # Startup: create tables if they do not exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed default group — skip for SQLite (used in tests) to avoid UUID type issues
    try:
        if engine.url.get_backend_name() != "sqlite":
            async with async_session_maker() as db:
                row = await db.get(GroupORM, DEFAULT_GROUP_ID)
                if not row:
                    db.add(GroupORM(id=DEFAULT_GROUP_ID, name=DEFAULT_GROUP_NAME))
                    await db.commit()
    except Exception:
        # Best-effort seeding only
        pass

    yield

    # Shutdown: dispose connection pool
    await engine.dispose()


app = FastAPI(title="Expense Service", lifespan=lifespan)

# Initialize tracing/instrumentation
try:
    init_tracing(app, sqlalchemy_engine=engine)
except Exception:
    # Observability should never block app startup
    pass

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(groups.router)
app.include_router(expenses.router)


@app.get("/")
async def read_root() -> dict[str, str]:
    """Health-check endpoint."""
    return {"status": "ok"}
