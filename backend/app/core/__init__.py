# backend/app/core/__init__.py
# Exports the two most-used core utilities so callers can write:
#   from app.core import settings, get_logger
from app.core.config import settings, get_settings  # noqa: F401
from app.core.logging import configure_logging, get_logger  # noqa: F401
