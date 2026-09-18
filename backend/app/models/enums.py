"""
backend/app/models/enums.py

All SQLAlchemy Enum types that mirror the six PostgreSQL enum types
defined in schema.sql.  Centralised here so every model file imports
from one location and enum names stay consistent across the codebase.

Rules:
  - Enum names (create_constraint=True, name=...) MUST match the
    PostgreSQL type names exactly.
  - Enum values MUST match the DDL values exactly.
  - Do NOT add, remove, or rename values.
"""

import enum

import sqlalchemy as sa


# ── PostgreSQL: flight_status ──────────────────────────────────────────────
class FlightStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    DELAYED = "DELAYED"
    CANCELLED = "CANCELLED"
    DEPARTED = "DEPARTED"


flight_status_enum = sa.Enum(
    FlightStatus,
    name="flight_status",
    create_type=True,        # let SQLAlchemy CREATE TYPE in PG
    values_callable=lambda e: [m.value for m in e],
)


# ── PostgreSQL: booking_status ─────────────────────────────────────────────
class BookingStatus(str, enum.Enum):
    CONFIRMED = "CONFIRMED"
    REBOOKED = "REBOOKED"
    CANCELLED = "CANCELLED"


booking_status_enum = sa.Enum(
    BookingStatus,
    name="booking_status",
    create_type=True,
    values_callable=lambda e: [m.value for m in e],
)


# ── PostgreSQL: priority_level ─────────────────────────────────────────────
class PriorityLevel(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    NORMAL = "NORMAL"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


priority_level_enum = sa.Enum(
    PriorityLevel,
    name="priority_level",
    create_type=True,
    values_callable=lambda e: [m.value for m in e],
)


# ── PostgreSQL: recommendation_status ─────────────────────────────────────
class RecommendationStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    EDITED = "EDITED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"


recommendation_status_enum = sa.Enum(
    RecommendationStatus,
    name="recommendation_status",
    create_type=True,
    values_callable=lambda e: [m.value for m in e],
)


# ── PostgreSQL: notification_status ───────────────────────────────────────
class NotificationStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    SENT = "SENT"
    FAILED = "FAILED"


notification_status_enum = sa.Enum(
    NotificationStatus,
    name="notification_status",
    create_type=True,
    values_callable=lambda e: [m.value for m in e],
)


# ── PostgreSQL: user_role ──────────────────────────────────────────────────
class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    OPERATIONS_AGENT = "OPERATIONS_AGENT"
    SUPERVISOR = "SUPERVISOR"


user_role_enum = sa.Enum(
    UserRole,
    name="user_role",
    create_type=True,
    values_callable=lambda e: [m.value for m in e],
)
