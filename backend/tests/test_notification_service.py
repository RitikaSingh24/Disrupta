"""
tests/test_notification_service.py

Tests for the notification service.

These tests focus on the notification service logic.
Due to database dependencies, these tests are designed to be lightweight and focused.
"""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.models.enums import NotificationStatus
from app.services.notification_service import build_notification_message


class MockPassenger:
    """Mock passenger object for testing."""
    def __init__(self, name):
        self.name = name


class MockFlight:
    """Mock flight object for testing."""
    def __init__(self, flight_number):
        self.flight_number = flight_number


class MockAlternativeFlight:
    """Mock alternative flight object for testing."""
    def __init__(self, flight_number):
        self.flight_number = flight_number


def test_build_notification_message_with_recommendation():
    """Test notification message generation with a recommended flight."""
    passenger = MockPassenger(name="Rahul Sharma")
    original_flight = MockFlight(flight_number="AA-100")
    recommended_flight = MockAlternativeFlight(flight_number="AI-305")
    priority = "HIGH"
    status = "APPROVED"
    reason = "Imminent connecting flight at 20:30"
    
    message = build_notification_message(
        passenger, original_flight, recommended_flight, priority, status, reason
    )
    
    assert "Rahul Sharma" in message
    assert "AA-100" in message
    assert "AI-305" in message
    assert "HIGH" in message
    assert "APPROVED" in message
    assert "Imminent connecting flight at 20:30" in message


def test_build_notification_message_without_recommendation():
    """Test notification message generation without a recommended flight."""
    passenger = MockPassenger(name="Priya")
    original_flight = MockFlight(flight_number="AA-100")
    recommended_flight = None
    priority = "NORMAL"
    status = "ESCALATED"
    reason = "No suitable alternative found"
    
    message = build_notification_message(
        passenger, original_flight, recommended_flight, priority, status, reason
    )
    
    assert "Priya" in message
    assert "AA-100" in message
    assert "None" in message
    assert "NORMAL" in message
    assert "ESCALATED" in message
    assert "No suitable alternative found" in message


def test_build_notification_message_deterministic():
    """Test that message generation is deterministic."""
    passenger = MockPassenger(name="Test Passenger")
    original_flight = MockFlight(flight_number="XY-123")
    recommended_flight = MockAlternativeFlight(flight_number="AB-456")
    priority = "MEDIUM"
    status = "PENDING"
    reason = "Test reason"
    
    message1 = build_notification_message(
        passenger, original_flight, recommended_flight, priority, status, reason
    )
    message2 = build_notification_message(
        passenger, original_flight, recommended_flight, priority, status, reason
    )
    
    assert message1 == message2


def test_build_notification_message_structure():
    """Test that the message has the expected structure."""
    passenger = MockPassenger(name="Test")
    original_flight = MockFlight(flight_number="AA-100")
    recommended_flight = MockAlternativeFlight(flight_number="AI-305")
    priority = "HIGH"
    status = "APPROVED"
    reason = "Test"
    
    message = build_notification_message(
        passenger, original_flight, recommended_flight, priority, status, reason
    )
    
    # Check for expected sections
    assert "Rebooking Update" in message
    assert "Passenger:" in message
    assert "Original Flight:" in message
    assert "Recommended Flight:" in message
    assert "Priority:" in message
    assert "Status:" in message
    assert "Reason:" in message