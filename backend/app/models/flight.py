"""
backend/app/models/flight.py

ORM model for the `flights` table.

DDL mirror:
    CREATE TABLE flights (
        flight_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        flight_number       VARCHAR(20) NOT NULL,
        airline             VARCHAR(80) NOT NULL,
        origin              VARCHAR(80) NOT NULL,
        destination         VARCHAR(80) NOT NULL,
        departure_time      TIMESTAMPTZ NOT NULL,
        arrival_time        TIMESTAMPTZ NOT NULL,
        status              flight_status NOT NULL DEFAULT 'SCHEDULED',
        cancellation_reason VARCHAR(255),
        total_seats         INTEGER NOT NULL DEFAULT 150,
        created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
    );

    CREATE INDEX idx_flights_status ON flights(status);
    CREATE INDEX idx_flights_route  ON flights(origin, destination);

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
from .enums import FlightStatus, flight_status_enum

if TYPE_CHECKING:
    from .booking import Booking
    from .alternative_flight import AlternativeFlight
    from .recommendation import RebookingRecommendation
    from .access_token import PassengerAccessToken


class Flight(Base):
    """Scheduled / disrupted flight operated by the airline."""

    __tablename__ = "flights"

    # ── Indexes (must match schema.sql exactly) ────────────────────────────
    __table_args__ = (
        sa.Index("idx_flights_status", "status"),
        sa.Index("idx_flights_route", "origin", "destination"),
    )

    # ── Primary key ────────────────────────────────────────────────────────
    flight_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )

    # ── Columns ────────────────────────────────────────────────────────────
    flight_number: Mapped[str] = mapped_column(sa.String(20), nullable=False)

    airline: Mapped[str] = mapped_column(sa.String(80), nullable=False)

    origin: Mapped[str] = mapped_column(sa.String(80), nullable=False)

    destination: Mapped[str] = mapped_column(sa.String(80), nullable=False)

    departure_time: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False
    )

    arrival_time: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False
    )

    status: Mapped[FlightStatus] = mapped_column(
        flight_status_enum,
        nullable=False,
        server_default="SCHEDULED",
    )

    cancellation_reason: Mapped[Optional[str]] = mapped_column(
        sa.String(255), nullable=True
    )

    total_seats: Mapped[int] = mapped_column(
        sa.Integer, nullable=False, server_default="150"
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
    # Bookings where this flight is the originally-booked flight
    bookings: Mapped[List["Booking"]] = relationship(
        "Booking",
        back_populates="flight",
        foreign_keys="Booking.flight_id",
    )

    # Bookings where this flight is the rebooked replacement flight
    rebooked_bookings: Mapped[List["Booking"]] = relationship(
        "Booking",
        back_populates="rebooked_flight",
        foreign_keys="Booking.rebooked_flight_id",
    )

    # Alternative flights that were linked to this original flight
    alternative_flights: Mapped[List["AlternativeFlight"]] = relationship(
        "AlternativeFlight",
        back_populates="linked_original_flight",
        foreign_keys="AlternativeFlight.linked_original_flight_id",
    )

    # Recommendations where this is the original disrupted flight
    recommendations_as_original: Mapped[List["RebookingRecommendation"]] = relationship(
        "RebookingRecommendation",
        back_populates="original_flight",
        foreign_keys="RebookingRecommendation.original_flight_id",
    )

    # Portal tokens linked to this flight
    access_tokens: Mapped[List["PassengerAccessToken"]] = relationship(
        "PassengerAccessToken",
        back_populates="flight",
        foreign_keys="PassengerAccessToken.flight_id",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<Flight id={self.flight_id} number={self.flight_number!r}"
            f" {self.origin}->{self.destination} status={self.status}>"
        )
