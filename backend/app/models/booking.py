"""
backend/app/models/booking.py

ORM model for the `bookings` table (passenger <-> flight many-to-many with payload).

DDL mirror:
    CREATE TABLE bookings (
        booking_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        passenger_id      UUID NOT NULL REFERENCES passengers(passenger_id) ON DELETE CASCADE,
        flight_id         UUID NOT NULL REFERENCES flights(flight_id) ON DELETE CASCADE,
        seat_number       VARCHAR(10),
        booking_class     VARCHAR(20) NOT NULL DEFAULT 'Economy',
        booking_status    booking_status NOT NULL DEFAULT 'CONFIRMED',
        rebooked_flight_id UUID REFERENCES flights(flight_id),
        created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
    );

    CREATE INDEX idx_bookings_flight     ON bookings(flight_id);
    CREATE INDEX idx_bookings_passenger  ON bookings(passenger_id);

IMPORTANT: `bookings` has TWO foreign keys that reference `flights`:
  - flight_id         → the originally booked flight   (ON DELETE CASCADE)
  - rebooked_flight_id → the replacement flight         (nullable, no cascade)

SQLAlchemy relationships are explicitly disambiguated via `foreign_keys=`.
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
from .enums import BookingStatus, booking_status_enum

if TYPE_CHECKING:
    from .passenger import Passenger
    from .flight import Flight
    from .connecting_flight import ConnectingFlight
    from .recommendation import RebookingRecommendation


class Booking(Base):
    """A passenger's confirmed seat on a flight, with optional rebooking pointer."""

    __tablename__ = "bookings"

    # ── Indexes ────────────────────────────────────────────────────────────
    __table_args__ = (
        sa.Index("idx_bookings_flight", "flight_id"),
        sa.Index("idx_bookings_passenger", "passenger_id"),
    )

    # ── Primary key ────────────────────────────────────────────────────────
    booking_id: Mapped[uuid.UUID] = mapped_column(
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

    flight_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("flights.flight_id", ondelete="CASCADE"),
        nullable=False,
    )

    seat_number: Mapped[Optional[str]] = mapped_column(sa.String(10), nullable=True)

    booking_class: Mapped[str] = mapped_column(
        sa.String(20),
        nullable=False,
        server_default="Economy",
    )

    booking_status: Mapped[BookingStatus] = mapped_column(
        booking_status_enum,
        nullable=False,
        server_default="CONFIRMED",
    )

    # Nullable — populated only after an agent-approved rebooking
    rebooked_flight_id: Mapped[Optional[uuid.UUID]] = mapped_column(
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
    passenger: Mapped["Passenger"] = relationship(
        "Passenger",
        back_populates="bookings",
        foreign_keys=[passenger_id],
    )

    # The originally-booked flight
    flight: Mapped["Flight"] = relationship(
        "Flight",
        back_populates="bookings",
        foreign_keys=[flight_id],
    )

    # The replacement flight (may be None until rebooked)
    rebooked_flight: Mapped[Optional["Flight"]] = relationship(
        "Flight",
        back_populates="rebooked_bookings",
        foreign_keys=[rebooked_flight_id],
    )

    # Connecting flights associated with this booking
    connecting_flights: Mapped[List["ConnectingFlight"]] = relationship(
        "ConnectingFlight",
        back_populates="booking",
        foreign_keys="ConnectingFlight.booking_id",
    )

    # Rebooking recommendations generated for this booking
    recommendations: Mapped[List["RebookingRecommendation"]] = relationship(
        "RebookingRecommendation",
        back_populates="booking",
        foreign_keys="RebookingRecommendation.booking_id",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<Booking id={self.booking_id} passenger={self.passenger_id}"
            f" flight={self.flight_id} status={self.booking_status}>"
        )
