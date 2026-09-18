"""
backend/app/models/passenger.py

ORM model for the `passengers` table.

DDL mirror:
    CREATE TABLE passengers (
        passenger_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name                    VARCHAR(120) NOT NULL,
        email                   VARCHAR(255) NOT NULL,
        phone                   VARCHAR(30),
        preferred_language      VARCHAR(40) NOT NULL DEFAULT 'English',
        special_requirement     TEXT,
        requirement_type        VARCHAR(60),
        requirement_declared_at TIMESTAMPTZ,
        created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at              TIMESTAMPTZ NOT NULL DEFAULT now()
    );

No indexes are declared on passengers in schema.sql — do not add any.
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
    from .booking import Booking
    from .connecting_flight import ConnectingFlight
    from .recommendation import RebookingRecommendation
    from .notification import Notification
    from .access_token import PassengerAccessToken


class Passenger(Base):
    """A traveller who holds a booking on a flight."""

    __tablename__ = "passengers"

    # ── Primary key ────────────────────────────────────────────────────────
    passenger_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )

    # ── Columns ────────────────────────────────────────────────────────────
    name: Mapped[str] = mapped_column(sa.String(120), nullable=False)

    email: Mapped[str] = mapped_column(sa.String(255), nullable=False)

    phone: Mapped[Optional[str]] = mapped_column(sa.String(30), nullable=True)

    preferred_language: Mapped[str] = mapped_column(
        sa.String(40),
        nullable=False,
        server_default="English",
    )

    # NULL until the passenger declares a requirement
    special_requirement: Mapped[Optional[str]] = mapped_column(
        sa.Text, nullable=True
    )

    # e.g. "Medical Appointment", "Business", "Family Emergency"
    requirement_type: Mapped[Optional[str]] = mapped_column(
        sa.String(60), nullable=True
    )

    requirement_declared_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
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
    bookings: Mapped[List["Booking"]] = relationship(
        "Booking",
        back_populates="passenger",
        foreign_keys="Booking.passenger_id",
    )

    connecting_flights: Mapped[List["ConnectingFlight"]] = relationship(
        "ConnectingFlight",
        back_populates="passenger",
        foreign_keys="ConnectingFlight.passenger_id",
    )

    recommendations: Mapped[List["RebookingRecommendation"]] = relationship(
        "RebookingRecommendation",
        back_populates="passenger",
        foreign_keys="RebookingRecommendation.passenger_id",
    )

    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="passenger",
        foreign_keys="Notification.passenger_id",
    )

    access_tokens: Mapped[List["PassengerAccessToken"]] = relationship(
        "PassengerAccessToken",
        back_populates="passenger",
        foreign_keys="PassengerAccessToken.passenger_id",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Passenger id={self.passenger_id} name={self.name!r}>"
