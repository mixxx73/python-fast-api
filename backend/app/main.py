from fastapi import FastAPI
from sqlalchemy.orm import sessionmaker

from .api import auth, expenses, groups, users
from .infrastructure.constants import DEFAULT_GROUP_ID, DEFAULT_GROUP_NAME
from .infrastructure.database import engine
from .infrastructure.orm import Base, GroupORM
from .observability import init_tracing

app = FastAPI(title="Expense Service")

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
def read_root() -> dict[str, str]:
    return {"status": "ok"}


@app.on_event("startup")
def on_startup() -> None:
    # Create database tables if they do not exist.
    Base.metadata.create_all(bind=engine)
    # Seed default group with hardcoded UUID if missing.
    # Skip when using SQLite (unit tests) to avoid UUID type affinity issues.
    try:
        if engine.url.get_backend_name() != "sqlite":
            SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
            db = SessionLocal()
            try:
                row = db.get(GroupORM, DEFAULT_GROUP_ID)
                if not row:
                    db.add(GroupORM(id=DEFAULT_GROUP_ID, name=DEFAULT_GROUP_NAME))
                    db.commit()
            finally:
                db.close()
    except Exception:
        # Best-effort seeding only
        pass
