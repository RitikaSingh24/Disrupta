"""
alembic/env.py

Alembic migration environment for IROP Passenger Rebooking Copilot.

Key points:
- DATABASE_URL is read from the OS environment (or a .env file via python-dotenv).
- target_metadata is set to Base.metadata so Alembic can auto-generate
  migrations by diffing the ORM models against the live database.
- Async engine is used (asyncpg driver) to match the rest of the stack.
"""

import asyncio
import os
from logging.config import fileConfig

from dotenv import load_dotenv  # pip install python-dotenv (already a transitive dep)
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# ── Load .env so DATABASE_URL is available ─────────────────────────────────
load_dotenv()

# ── Alembic Config object ──────────────────────────────────────────────────
config = context.config

# Inject DATABASE_URL from environment into the alembic config at runtime.
# This avoids hardcoding credentials in alembic.ini.
config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

# ── Python logging setup ───────────────────────────────────────────────────
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── ORM metadata — the single source of truth ─────────────────────────────
# Importing Base (and all models via __init__.py) registers every table
# in Base.metadata so Alembic can diff them.
from app.models import Base  # noqa: E402  (import after env setup intentional)

target_metadata = Base.metadata


# ── Offline migrations (no live DB connection) ─────────────────────────────
def run_migrations_offline() -> None:
    """Generate SQL script without connecting to the database."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Render PostgreSQL-native enum types correctly
        include_schemas=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Online migrations (connects to the live database) ─────────────────────
def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_schemas=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


# ── Entry point ────────────────────────────────────────────────────────────
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
