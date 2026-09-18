"""
backend/app/core/config.py

Application settings loaded from the .env file via pydantic-settings.

Usage (anywhere in the app):
    from app.core.config import settings
    print(settings.DATABASE_URL)

Rules:
  - All env vars are declared here with types and defaults.
  - Never read os.environ directly elsewhere — always go through settings.
  - This file contains NO business logic, NO database calls.
"""

from functools import lru_cache
from typing import List

from pydantic import AnyUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    All configuration values for the IROP Rebooking Copilot backend.
    Values are read from environment variables (or a .env file in the
    backend/ directory).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",       # ignore unknown env vars — avoids accidental errors
    )

    # ── Database ───────────────────────────────────────────────────────────
    DATABASE_URL: str
    # Must be the asyncpg URI form:
    # postgresql+asyncpg://<user>:<pass>@<host>:6543/postgres

    # ── JWT ────────────────────────────────────────────────────────────────
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 120

    # ── OpenAI ────────────────────────────────────────────────────────────
    OPENAI_API_KEY: str = ""

    # ── Feature flags ──────────────────────────────────────────────────────
    USE_AI_REASONING: bool = False  # safe default — rule engine only

    # ── CORS ───────────────────────────────────────────────────────────────
    # Comma-separated origins in .env:
    # CORS_ORIGINS=http://localhost:5173,https://my-app.vercel.app
    CORS_ORIGINS: List[str] | str = ["http://localhost:5173"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Accept both a comma-separated string and a JSON list."""
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # ── Passenger portal ───────────────────────────────────────────────────
    PORTAL_TOKEN_EXPIRY_HOURS: int = 72

    # ── Application ────────────────────────────────────────────────────────
    APP_NAME: str = "IROP Passenger Rebooking Copilot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return a cached singleton Settings instance.

    Use this everywhere instead of instantiating Settings() directly,
    so there is only one read of the .env file per process.
    """
    return Settings()


# Convenience alias — import this directly in most places
settings: Settings = get_settings()
