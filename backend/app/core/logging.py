"""
backend/app/core/logging.py

Centralised logging configuration for the IROP Rebooking Copilot.

Call configure_logging() once at application startup (in main.py).
After that, anywhere in the codebase:

    import logging
    logger = logging.getLogger(__name__)
    logger.info("Something happened")

Design decisions:
  - Structured JSON logging in production (DEBUG=False) for log-aggregation
    tools like Datadog / CloudWatch.
  - Plain human-readable format in development (DEBUG=True) so the terminal
    is easy to read during the 24-hour build.
  - SQLAlchemy engine noise is suppressed to WARNING by default.
  - No third-party logging libs required — uses stdlib only.
"""

import logging
import logging.config
import sys
from typing import Any

# ── Formatters ─────────────────────────────────────────────────────────────

_DEV_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DEV_DATE_FORMAT = "%H:%M:%S"

# Minimal JSON-ish format — replace with `python-json-logger` in production
_PROD_FORMAT = (
    '{"time":"%(asctime)s","level":"%(levelname)s",'
    '"logger":"%(name)s","msg":"%(message)s"}'
)


def configure_logging(debug: bool = False) -> None:
    """
    Call once at FastAPI startup.

    Args:
        debug: If True, use human-readable format + DEBUG level.
               If False, use compact JSON format + INFO level.
    """
    root_level = logging.DEBUG if debug else logging.INFO
    fmt = _DEV_FORMAT if debug else _PROD_FORMAT
    date_fmt = _DEV_DATE_FORMAT if debug else "%Y-%m-%dT%H:%M:%SZ"

    logging_config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": fmt,
                "datefmt": date_fmt,
            },
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "default",
            },
        },
        "root": {
            "level": root_level,
            "handlers": ["stdout"],
        },
        "loggers": {
            # Suppress noisy SQLAlchemy engine logs unless DEBUG
            "sqlalchemy.engine": {
                "level": logging.DEBUG if debug else logging.WARNING,
                "propagate": True,
            },
            # Keep uvicorn access logs at INFO always
            "uvicorn.access": {
                "level": logging.INFO,
                "propagate": True,
            },
            # Our own app namespace
            "app": {
                "level": root_level,
                "propagate": True,
            },
        },
    }

    logging.config.dictConfig(logging_config)


def get_logger(name: str) -> logging.Logger:
    """
    Convenience wrapper — equivalent to logging.getLogger(name).
    Preferred style within this project:

        from app.core.logging import get_logger
        logger = get_logger(__name__)
    """
    return logging.getLogger(name)
