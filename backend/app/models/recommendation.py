"""
backend/app/models/recommendation.py

ORM model for the `rebooking_recommendations` table.

DDL mirror:
    CREATE TABLE rebooking_recommendations (
        recommendation_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        passenger_id         UUID NOT NULL REFERENCES passengers(passenger_id) ON DELETE CASCADE,
        booking_id           UUID NOT NULL REFERENCES bookings(booking_id) ON DELETE CASCADE,
        original_flight_id   UUID NOT NULL REFERENCES flights(flight_id),
        recommended_flight_id UUID REFERENCES alternative_flights(alternative_flight_id),
        priority             priority_level NOT NULL,
        reason               TEXT NOT NULL,
        status               recommendation_status NOT NULL DEFAULT 'PENDING',
        reviewed_by_user_id  UUID REFERENCES users(user_id),
        reviewed_at          TIMESTAMPTZ,
        version              INTEGER NOT NULL DEFAULT 1,
        created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at           TIMESTAMPTZ NOT NULL DEFAULT now()
    );

    CREATE INDEX idx_recs_passenger ON rebooking_recommendations(passenger_id);
    CREATE INDEX idx_recs_status    ON rebooking_recommendations(status);

IMPORTANT: `rebooking_recommendations` has TWO foreign keys that reference `flights`:
  - original_flight_id   (NOT NULL, no cascade)
  … and separately references `alternative_flights`:
  - recommended_flight_id (nullable)
All relationships are explicitly disambiguated.
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
from .enums import PriorityLevel, priority_level_enum, RecommendationStatus, recommendation_status_enum

if TYPE_CHECKING:
    from .passenger import Passenger
    from .booking import Booking
    from .flight import Flight
    from .alternative_flight import AlternativeFlight
    from .user import User
    from .notification import Notification


class RebookingRecommendation(Base):
    """AI- or rule-generated rebooking recommendation awaiting human review."""

    __tablename__ = "rebooking_recommendations"

    # ── Indexes ────────────────────────────────────────────────────────────
    __table_args__ = (
        sa.Index("idx_recs_passenger", "passenger_id"),
        sa.Index("idx_recs_status", "status"),
    )

    # ── Primary key ────────────────────────────────────────────────────────
    recommendation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )

    # ── Columns ────────────────────────────────────────────────────────────
    passenger_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("passengers.passenger_id", ondelete="CASCADE"),
        nullable=False,
    )

    booking_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("bookings.booking_id", ondelete="CASCADE"),
        nullable=False,
    )

    original_flight_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("flights.flight_id"),   # no ondelete — matches DDL
        nullable=False,
    )

    # Nullable — None when no viable alternative is found (escalated)
    recommended_flight_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("alternative_flights.alternative_flight_id"),
        nullable=True,
    )

    priority: Mapped[PriorityLevel] = mapped_column(
        priority_level_enum, nullable=False
    )

    # Human-readable rule/AI-generated explanation
    reason: Mapped[str] = mapped_column(sa.Text, nullable=False)

    status: Mapped[RecommendationStatus] = mapped_column(
        recommendation_status_enum,
        nullable=False,
        server_default="PENDING",
    )

    # Set when an employee approves/edits/rejects
    reviewed_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("users.user_id"),   # no ondelete — matches DDL
        nullable=True,
    )

    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )

    # Bumped on each re-analysis (e.g. after passenger declares a requirement)
    version: Mapped[int] = mapped_column(
        sa.Integer, nullable=False, server_default="1"
    )

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )

    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )

    # ── Relationships ──────────────────────────────────────────────────────
    passenger: Mapped["Passenger"] = relationship(
        "Passenger",
        back_populates="recommendations",
        foreign_keys=[passenger_id],
    )

    booking: Mapped["Booking"] = relationship(
        "Booking",
        back_populates="recommendations",
        foreign_keys=[booking_id],
    )

    original_flight: Mapped["Flight"] = relationship(
        "Flight",
        back_populates="recommendations_as_original",
        foreign_keys=[original_flight_id],
    )

    recommended_flight: Mapped[Optional["AlternativeFlight"]] = relationship(
        "AlternativeFlight",
        back_populates="recommendations",
        foreign_keys=[recommended_flight_id],
    )

    reviewed_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="reviewed_recommendations",
        foreign_keys=[reviewed_by_user_id],
    )

    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="recommendation",
        foreign_keys="Notification.recommendation_id",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<RebookingRecommendation id={self.recommendation_id}"
            f" passenger={self.passenger_id} priority={self.priority}"
            f" status={self.status} v={self.version}>"
        )
