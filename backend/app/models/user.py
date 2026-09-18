"""
backend/app/models/user.py

ORM model for the `users` table (employees).

DDL mirror:
    CREATE TABLE users (
        user_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name          VARCHAR(120) NOT NULL,
        email         VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        role          user_role NOT NULL DEFAULT 'OPERATIONS_AGENT',
        created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
    );

No business logic.  No queries.  No auth helpers.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enums import UserRole, user_role_enum

if TYPE_CHECKING:
    # Avoid circular imports at runtime; used only for type-checker hints.
    from .recommendation import RebookingRecommendation


class User(Base):
    """Employee / operator account."""

    __tablename__ = "users"

    # ── Primary key ────────────────────────────────────────────────────────
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )

    # ── Columns ────────────────────────────────────────────────────────────
    name: Mapped[str] = mapped_column(sa.String(120), nullable=False)

    email: Mapped[str] = mapped_column(
        sa.String(255),
        unique=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(sa.String(255), nullable=False)

    role: Mapped[UserRole] = mapped_column(
        user_role_enum,
        nullable=False,
        server_default="OPERATIONS_AGENT",
    )

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )

    # ── Relationships (back-refs from other tables) ────────────────────────
    reviewed_recommendations: Mapped[List["RebookingRecommendation"]] = relationship(
        "RebookingRecommendation",
        back_populates="reviewed_by_user",
        foreign_keys="RebookingRecommendation.reviewed_by_user_id",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User id={self.user_id} email={self.email!r} role={self.role}>"
