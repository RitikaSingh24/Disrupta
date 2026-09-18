"""
backend/app/models/connecting_flight.py

ORM model for the `connecting_flights` table.

DDL mirror:
    CREATE TABLE connecting_flights (
        connection_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        passenger_id   UUID NOT NULL REFERENCES passengers(passenger_id) ON DELETE CASCADE,
        booking_id     UUID REFERENCES bookings(booking_id) ON DELETE CASCADE,
        flight_number  VARCHAR(20) NOT NULL,
        departure_time TIMESTAMPTZ NOT NULL,
        destination    VARCHAR(80) NOT NULL,
        created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
    );

    CREATE INDEX idx_connections_passenger ON connecting_flights(passenger_id);

No business logic.  No queries.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .passenger import Passenger
    from .booking import Booking


class ConnectingFlight(Base):
    """A connecting flight declared by or on behalf of a passenger."""

    __tablename__ = "connecting_flights"

    # ── Indexes ────────────────────────────────────────────────────────────
    __table_args__ = (
        sa.Index("idx_connections_passenger", "passenger_id"),
    )

    # ── Primary key ────────────────────────────────────────────────────────
    connection_id: Mapped[uuid.UUID] = mapped_column(
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

    # booking_id is nullable per DDL (REFERENCES … ON DELETE CASCADE, no NOT NULL)
    booking_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("bookings.booking_id", ondelete="CASCADE"),
        nullable=True,
    )

    flight_number: Mapped[str] = mapped_column(sa.String(20), nullable=False)

    departure_time: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False
    )

    destination: Mapped[str] = mapped_column(sa.String(80), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )

    # ── Relationships ──────────────────────────────────────────────────────
    passenger: Mapped["Passenger"] = relationship(
        "Passenger",
        back_populates="connecting_flights",
        foreign_keys=[passenger_id],
    )

    booking: Mapped[Optional["Booking"]] = relationship(
        "Booking",
        back_populates="connecting_flights",
        foreign_keys=[booking_id],
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<ConnectingFlight id={self.connection_id}"
            f" flight={self.flight_number!r} -> {self.destination!r}>"
        )
