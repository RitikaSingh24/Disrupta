"""
backend/app/models/notification.py

ORM model for the `notifications` table.

DDL mirror:
    CREATE TABLE notifications (
        notification_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        passenger_id     UUID NOT NULL REFERENCES passengers(passenger_id) ON DELETE CASCADE,
        recommendation_id UUID REFERENCES rebooking_recommendations(recommendation_id),
        language         VARCHAR(40) NOT NULL DEFAULT 'English',
        message          TEXT NOT NULL,
        status           notification_status NOT NULL DEFAULT 'DRAFT',
        created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
        sent_at          TIMESTAMPTZ
    );

    CREATE INDEX idx_notifications_passenger ON notifications(passenger_id);

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
from .enums import NotificationStatus, notification_status_enum

if TYPE_CHECKING:
    from .passenger import Passenger
    from .recommendation import RebookingRecommendation


class Notification(Base):
    """A drafted or sent passenger notification message."""

    __tablename__ = "notifications"

    # ── Indexes ────────────────────────────────────────────────────────────
    __table_args__ = (
        sa.Index("idx_notifications_passenger", "passenger_id"),
    )

    # ── Primary key ────────────────────────────────────────────────────────
    notification_id: Mapped[uuid.UUID] = mapped_column(
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

    # Nullable — a notification may be generated before a recommendation exists
    recommendation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("rebooking_recommendations.recommendation_id"),
        nullable=True,
    )

    language: Mapped[str] = mapped_column(
        sa.String(40),
        nullable=False,
        server_default="English",
    )

    message: Mapped[str] = mapped_column(sa.Text, nullable=False)

    status: Mapped[NotificationStatus] = mapped_column(
        notification_status_enum,
        nullable=False,
        server_default="DRAFT",
    )

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("now()"),
    )

    # Populated when status transitions to SENT
    sent_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )

    # ── Relationships ──────────────────────────────────────────────────────
    passenger: Mapped["Passenger"] = relationship(
        "Passenger",
        back_populates="notifications",
        foreign_keys=[passenger_id],
    )

    recommendation: Mapped[Optional["RebookingRecommendation"]] = relationship(
        "RebookingRecommendation",
        back_populates="notifications",
        foreign_keys=[recommendation_id],
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<Notification id={self.notification_id}"
            f" passenger={self.passenger_id}"
            f" lang={self.language!r} status={self.status}>"
        )
