"""
backend/app/models/alternative_flight.py

ORM model for the `alternative_flights` table.

DDL mirror:
    CREATE TABLE alternative_flights (
        alternative_flight_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        flight_number            VARCHAR(20) NOT NULL,
        origin                   VARCHAR(80) NOT NULL,
        destination              VARCHAR(80) NOT NULL,
        departure_time           TIMESTAMPTZ NOT NULL,
        arrival_time             TIMESTAMPTZ NOT NULL,
        available_seats          INTEGER NOT NULL DEFAULT 0,
        linked_original_flight_id UUID REFERENCES flights(flight_id),
        created_at               TIMESTAMPTZ NOT NULL DEFAULT now()
    );

    CREATE INDEX idx_alt_flights_route ON alternative_flights(origin, destination);

No business logic.  No queries.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .flight import Flight
    from .recommendation import RebookingRecommendation


class AlternativeFlight(Base):
    """A candidate flight that can replace a cancelled/delayed original flight."""

    __tablename__ = "alternative_flights"

    # ── Indexes ────────────────────────────────────────────────────────────
    __table_args__ = (
        sa.Index("idx_alt_flights_route", "origin", "destination"),
    )

    # ── Primary key ────────────────────────────────────────────────────────
    alternative_flight_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )

    # ── Columns ────────────────────────────────────────────────────────────
    flight_number: Mapped[str] = mapped_column(sa.String(20), nullable=False)

    origin: Mapped[str] = mapped_column(sa.String(80), nullable=False)

    destination: Mapped[str] = mapped_column(sa.String(80), nullable=False)

    departure_time: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False
    )

    arrival_time: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False
    )

    available_seats: Mapped[int] = mapped_column(
        sa.Integer, nullable=False, server_default="0"
    )

    # Nullable — links back to the disrupted flight for easy querying
    linked_original_flight_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("flights.flight_id"),   # no ondelete — matches DDL
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )

    # ── Relationships ──────────────────────────────────────────────────────
    linked_original_flight: Mapped[Optional["Flight"]] = relationship(
        "Flight",
        back_populates="alternative_flights",
        foreign_keys=[linked_original_flight_id],
    )

    # Recommendations that suggest this alternative flight
    recommendations: Mapped[List["RebookingRecommendation"]] = relationship(
        "RebookingRecommendation",
        back_populates="recommended_flight",
        foreign_keys="RebookingRecommendation.recommended_flight_id",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<AlternativeFlight id={self.alternative_flight_id}"
            f" number={self.flight_number!r}"
            f" {self.origin}->{self.destination}"
            f" seats={self.available_seats}>"
        )
