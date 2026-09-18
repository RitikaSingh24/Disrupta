# backend/app/db/__init__.py
# Convenience re-exports for the db package.
# Routers and services should import from here, not from sub-modules directly.
from app.db.session import AsyncSessionLocal, db_session, engine, get_db  # noqa: F401
from app.db.base import Base  # noqa: F401
