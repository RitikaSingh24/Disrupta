"""
backend/app/models/access_token.py

ORM model for the `passenger_access_tokens` table.

DDL mirror:
    CREATE TABLE passenger_access_tokens (
        token        VARCHAR(64) PRIMARY KEY,
        passenger_id UUID NOT NULL REFERENCES passengers(passenger_id) ON DELETE CASCADE,
        flight_id    UUID NOT NULL REFERENCES flights(flight_id),
        expires_at   TIMESTAMPTZ NOT NULL,
        used         BOOLEAN NOT NULL DEFAULT FALSE,
        created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
    );

NOTE: The primary key `token` is VARCHAR(64) — NOT a UUID.
      It holds a secrets.token_urlsafe(32) value generated in Python.
      Do NOT replace it with an integer or UUID column.

No business logic.  No queries.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .passenger import Passenger
    from .flight import Flight


class PassengerAccessToken(Base):
    """
    Time-limited, single-use token embedded in a passenger portal link.
    No database index beyond the PK — matches schema.sql exactly.
    """

    __tablename__ = "passenger_access_tokens"

    # ── Primary key — VARCHAR(64), NOT a UUID ──────────────────────────────
    token: Mapped[str] = mapped_column(sa.String(64), primary_key=True)

    # ── Columns ────────────────────────────────────────────────────────────
    passenger_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("passengers.passenger_id", ondelete="CASCADE"),
        nullable=False,
    )

    flight_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("flights.flight_id"),   # no ondelete — matches DDL
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False
    )

    used: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, server_default=sa.false()
    )

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )

    # ── Relationships ──────────────────────────────────────────────────────
    passenger: Mapped["Passenger"] = relationship(
        "Passenger",
        back_populates="access_tokens",
        foreign_keys=[passenger_id],
    )

    flight: Mapped["Flight"] = relationship(
        "Flight",
        back_populates="access_tokens",
        foreign_keys=[flight_id],
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<PassengerAccessToken token={self.token[:8]}…"
            f" passenger={self.passenger_id}"
            f" used={self.used} expires={self.expires_at}>"
        )
