"""
backend/app/db/session.py

Async SQLAlchemy engine + session factory + FastAPI dependency.

Responsibilities:
  - Create one AsyncEngine per process (reused across requests).
  - Provide an AsyncSessionLocal factory for direct use in scripts/seed.
  - Expose get_db() as a FastAPI dependency that yields a session and
    commits/rolls back automatically.

What this file does NOT do:
  - It does not define ORM models.
  - It does not run queries.
  - It does not perform migrations.

Usage in a FastAPI router:
    from app.db.session import get_db
    from sqlalchemy.ext.asyncio import AsyncSession

    @router.get("/example")
    async def example(db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(MyModel))
        return result.scalars().all()

Usage in a seed script / one-off task:
    from app.db.session import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        session.add(some_object)
        await session.commit()
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

# ── Engine (one per process) ───────────────────────────────────────────────
# echo=True only in DEBUG — prints every SQL statement to stdout.
# pool_pre_ping=True drops stale connections (important for Supabase pooler).
# connect_args disables statement caching for Supabase pgBouncer
# which runs in transaction mode and does not support named prepared statements.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    # Supabase pgBouncer runs in transaction mode — use minimal pool
    pool_size=1,
    max_overflow=0,
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
        "prepared_statement_name_func": lambda: "",
    },
)

# ── Session factory ────────────────────────────────────────────────────────
# expire_on_commit=False is important for async: prevents SQLAlchemy from
# issuing extra SELECTs after commit when you access already-loaded attrs.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ── FastAPI dependency ─────────────────────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Yield an async database session scoped to a single HTTP request.

    Commits on success, rolls back on any exception, always closes.
    Inject into route handlers with:  db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ── Utility context manager (for scripts / tests) ─────────────────────────
@asynccontextmanager
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for use outside FastAPI (seed scripts, tests).

    Example:
        async with db_session() as session:
            session.add(obj)
            await session.commit()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
