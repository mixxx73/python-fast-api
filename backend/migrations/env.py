from __future__ import annotations

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# This is the Alembic Config object, which provides access to
# the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Ensure project root is on PYTHONPATH when Alembic runs from migrations dir
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Override sqlalchemy.url from env DATABASE_URL if present
db_url = os.getenv("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

# Import metadata from the app
from app.infrastructure.orm import Base  # noqa: E402

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # Use async engine when the URL uses an async driver (e.g. postgresql+asyncpg).
    # This avoids "greenlet_spawn has not been called" errors when Alembic calls
    # into SQLAlchemy async drivers.
    from sqlalchemy.ext.asyncio import create_async_engine
    import asyncio

    url = config.get_main_option("sqlalchemy.url")

    if url and url.startswith("postgresql+asyncpg"):
        async_engine = create_async_engine(
            url,
            poolclass=pool.NullPool,
            future=True,
        )

        def _run_migrations(connection):
            context.configure(connection=connection, target_metadata=target_metadata)
            with context.begin_transaction():
                context.run_migrations()

        async def do_run():
            async with async_engine.connect() as connection:
                await connection.run_sync(_run_migrations)

        asyncio.run(do_run())
    else:
        # Fallback to the synchronous engine for non-async DB URLs
        connectable = engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        with connectable.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)

            with context.begin_transaction():
                context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
