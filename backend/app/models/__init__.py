"""
backend/app/models/__init__.py

Public surface of the models package.

Import every ORM class (and the shared Base) from here so that:
  - Alembic's env.py can do:  from app.models import Base
  - FastAPI startup can do:   from app.models import User, Flight, …
  - CRUD / service layers never need to know the internal file structure.

Rules:
  - No business logic in this file.
  - No database queries.
  - No FastAPI endpoints.
  - No authentication code.
  - Imports only — nothing else.
"""

# ── Shared declarative base ────────────────────────────────────────────────
from .base import Base  # noqa: F401  (re-exported for Alembic target_metadata)

# ── Enums (Python + SQLAlchemy representations) ───────────────────────────
from .enums import (  # noqa: F401
    FlightStatus,
    BookingStatus,
    PriorityLevel,
    RecommendationStatus,
    NotificationStatus,
    UserRole,
    flight_status_enum,
    booking_status_enum,
    priority_level_enum,
    recommendation_status_enum,
    notification_status_enum,
    user_role_enum,
)

# ── ORM models (import order respects FK dependency depth) ─────────────────
# Leaf / no-dependency tables first, then tables that reference them.

from .user import User  # noqa: F401
# users has no FK dependencies.

from .flight import Flight  # noqa: F401
# flights has no FK dependencies.

from .passenger import Passenger  # noqa: F401
# passengers has no FK dependencies.

from .booking import Booking  # noqa: F401
# bookings → passengers, flights (×2)

from .connecting_flight import ConnectingFlight  # noqa: F401
# connecting_flights → passengers, bookings

from .alternative_flight import AlternativeFlight  # noqa: F401
# alternative_flights → flights

from .recommendation import RebookingRecommendation  # noqa: F401
# rebooking_recommendations → passengers, bookings, flights, alternative_flights, users

from .notification import Notification  # noqa: F401
# notifications → passengers, rebooking_recommendations

from .access_token import PassengerAccessToken  # noqa: F401
# passenger_access_tokens → passengers, flights

# ── Convenience list (useful for iteration in tests or migrations) ─────────
__all__ = [
    # base
    "Base",
    # enums — Python
    "FlightStatus",
    "BookingStatus",
    "PriorityLevel",
    "RecommendationStatus",
    "NotificationStatus",
    "UserRole",
    # enums — SQLAlchemy
    "flight_status_enum",
    "booking_status_enum",
    "priority_level_enum",
    "recommendation_status_enum",
    "notification_status_enum",
    "user_role_enum",
    # ORM models
    "User",
    "Flight",
    "Passenger",
    "Booking",
    "ConnectingFlight",
    "AlternativeFlight",
    "RebookingRecommendation",
    "Notification",
    "PassengerAccessToken",
]
