"""
backend/app/db/base.py

ORM metadata aggregator — the ONLY import Alembic needs.

Purpose:
  Import Base and every ORM model so that Base.metadata contains all table
  definitions. This lets Alembic's env.py do a single import:

      from app.db.base import Base
      target_metadata = Base.metadata

Rules:
  - This file NEVER creates an engine or session.
  - This file NEVER runs queries.
  - Add new model imports here as new models are created in app/models/.
"""

# Re-export the shared declarative base
from app.models.base import Base  # noqa: F401

# ── Import every model so SQLAlchemy registers their tables in Base.metadata ─
# Order: no-dependency tables first (leaf nodes), then tables with FKs.
from app.models.user import User  # noqa: F401
from app.models.flight import Flight  # noqa: F401
from app.models.passenger import Passenger  # noqa: F401
from app.models.booking import Booking  # noqa: F401
from app.models.connecting_flight import ConnectingFlight  # noqa: F401
from app.models.alternative_flight import AlternativeFlight  # noqa: F401
from app.models.recommendation import RebookingRecommendation  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.access_token import PassengerAccessToken  # noqa: F401

# Expose __all__ so static analysis tools understand what this module provides
__all__ = [
    "Base",
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
