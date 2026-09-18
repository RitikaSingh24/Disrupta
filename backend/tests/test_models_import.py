"""
tests/test_models_import.py

Smoke test: verifies that every ORM model and enum can be imported cleanly
from the models package without requiring a database connection.

Run with:
    cd backend
    pytest tests/test_models_import.py -v
"""

import pytest

# ── If these imports succeed, the package structure is correct ─────────────
from app.models import (
    Base,
    # enums
    FlightStatus,
    BookingStatus,
    PriorityLevel,
    RecommendationStatus,
    NotificationStatus,
    UserRole,
    # ORM models
    User,
    Flight,
    Passenger,
    Booking,
    ConnectingFlight,
    AlternativeFlight,
    RebookingRecommendation,
    Notification,
    PassengerAccessToken,
)


class TestModelsImport:
    """Verify the models package exports the expected symbols."""

    def test_base_is_declarative_base(self):
        from sqlalchemy.orm import DeclarativeBase
        assert issubclass(Base, DeclarativeBase)

    def test_all_tables_registered(self):
        table_names = set(Base.metadata.tables.keys())
        expected = {
            "users",
            "flights",
            "passengers",
            "bookings",
            "connecting_flights",
            "alternative_flights",
            "rebooking_recommendations",
            "notifications",
            "passenger_access_tokens",
        }
        assert expected == table_names, (
            f"Missing tables: {expected - table_names}  |  "
            f"Extra tables: {table_names - expected}"
        )

    def test_flight_status_values(self):
        assert {e.value for e in FlightStatus} == {
            "SCHEDULED", "DELAYED", "CANCELLED", "DEPARTED"
        }

    def test_booking_status_values(self):
        assert {e.value for e in BookingStatus} == {
            "CONFIRMED", "REBOOKED", "CANCELLED"
        }

    def test_priority_level_values(self):
        assert {e.value for e in PriorityLevel} == {
            "HIGH", "MEDIUM", "NORMAL", "REVIEW_REQUIRED"
        }

    def test_recommendation_status_values(self):
        assert {e.value for e in RecommendationStatus} == {
            "PENDING", "APPROVED", "EDITED", "REJECTED", "ESCALATED"
        }

    def test_notification_status_values(self):
        assert {e.value for e in NotificationStatus} == {
            "DRAFT", "PENDING_REVIEW", "APPROVED", "SENT", "FAILED"
        }

    def test_user_role_values(self):
        assert {e.value for e in UserRole} == {
            "ADMIN", "OPERATIONS_AGENT", "SUPERVISOR"
        }

    def test_users_columns(self):
        cols = {c.name for c in User.__table__.columns}
        assert cols == {"user_id", "name", "email", "password_hash", "role", "created_at"}

    def test_flights_columns(self):
        cols = {c.name for c in Flight.__table__.columns}
        assert cols == {
            "flight_id", "flight_number", "airline", "origin", "destination",
            "departure_time", "arrival_time", "status", "cancellation_reason",
            "total_seats", "created_at", "updated_at",
        }

    def test_passengers_columns(self):
        cols = {c.name for c in Passenger.__table__.columns}
        assert cols == {
            "passenger_id", "name", "email", "phone", "preferred_language",
            "special_requirement", "requirement_type", "requirement_declared_at",
            "created_at", "updated_at",
        }

    def test_bookings_columns(self):
        cols = {c.name for c in Booking.__table__.columns}
        assert cols == {
            "booking_id", "passenger_id", "flight_id", "seat_number",
            "booking_class", "booking_status", "rebooked_flight_id", "created_at",
        }

    def test_connecting_flights_columns(self):
        cols = {c.name for c in ConnectingFlight.__table__.columns}
        assert cols == {
            "connection_id", "passenger_id", "booking_id",
            "flight_number", "departure_time", "destination", "created_at",
        }

    def test_alternative_flights_columns(self):
        cols = {c.name for c in AlternativeFlight.__table__.columns}
        assert cols == {
            "alternative_flight_id", "flight_number", "origin", "destination",
            "departure_time", "arrival_time", "available_seats",
            "linked_original_flight_id", "created_at",
        }

    def test_recommendations_columns(self):
        cols = {c.name for c in RebookingRecommendation.__table__.columns}
        assert cols == {
            "recommendation_id", "passenger_id", "booking_id",
            "original_flight_id", "recommended_flight_id",
            "priority", "reason", "status",
            "reviewed_by_user_id", "reviewed_at",
            "version", "created_at", "updated_at",
        }

    def test_notifications_columns(self):
        cols = {c.name for c in Notification.__table__.columns}
        assert cols == {
            "notification_id", "passenger_id", "recommendation_id",
            "language", "message", "status", "created_at", "sent_at",
        }

    def test_access_tokens_columns(self):
        cols = {c.name for c in PassengerAccessToken.__table__.columns}
        assert cols == {
            "token", "passenger_id", "flight_id",
            "expires_at", "used", "created_at",
        }

    def test_access_token_pk_is_string_not_uuid(self):
        """token PK must be VARCHAR(64), not a UUID column."""
        import sqlalchemy as sa
        pk_col = PassengerAccessToken.__table__.c.token
        assert isinstance(pk_col.type, sa.String)
        assert pk_col.type.length == 64

    def test_indexes_present(self):
        all_indexes = {
            idx.name
            for tbl in Base.metadata.tables.values()
            for idx in tbl.indexes
        }
        required = {
            "idx_flights_status",
            "idx_flights_route",
            "idx_bookings_flight",
            "idx_bookings_passenger",
            "idx_connections_passenger",
            "idx_alt_flights_route",
            "idx_recs_passenger",
            "idx_recs_status",
            "idx_notifications_passenger",
        }
        missing = required - all_indexes
        assert not missing, f"Missing indexes: {missing}"
