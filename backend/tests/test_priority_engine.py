"""
tests/test_priority_engine.py

Tests for the pure priority scoring engine.

These tests focus on business logic and do NOT require:
- network
- OpenAI
- Supabase
- external APIs
- LLMs
"""

from datetime import datetime, timedelta, timezone

import pytest

from app.models.enums import PriorityLevel
from app.services.priority_engine import (
    HIGH_CONNECTION_THRESHOLD_HOURS,
    MEDIUM_CONNECTION_THRESHOLD_HOURS,
    score_priority,
)


class MockPassenger:
    """Mock passenger object for testing."""
    def __init__(self, special_requirement=None):
        self.special_requirement = special_requirement


class MockConnectingFlight:
    """Mock connecting flight object for testing."""
    def __init__(self, departure_time):
        self.departure_time = departure_time


class MockCancelledFlight:
    """Mock cancelled flight object for testing."""
    def __init__(self, departure_time):
        self.departure_time = departure_time


def test_special_requirement_high_priority():
    """Case 1: Passenger with special requirement gets HIGH priority."""
    passenger = MockPassenger(special_requirement="Wheelchair assistance needed")
    connecting_flights = []
    cancelled_flight = MockCancelledFlight(departure_time=datetime.now(timezone.utc))
    
    priority, reason = score_priority(passenger, connecting_flights, cancelled_flight)
    
    assert priority == PriorityLevel.HIGH
    assert "Wheelchair assistance needed" in reason
    assert "declared" in reason


def test_rahul_imminent_connection_high_priority():
    """Case 2: Rahul has ~2.5 hour connection - should be HIGH priority."""
    # Setup: Cancelled flight at 6:00 PM, connecting flight at 8:30 PM (2.5 hours)
    cancelled_departure = datetime(2024, 1, 15, 18, 0, 0, tzinfo=timezone.utc)
    connecting_departure = datetime(2024, 1, 15, 20, 30, 0, tzinfo=timezone.utc)
    
    passenger = MockPassenger(special_requirement=None)
    connecting_flights = [MockConnectingFlight(departure_time=connecting_departure)]
    cancelled_flight = MockCancelledFlight(departure_time=cancelled_departure)
    
    priority, reason = score_priority(passenger, connecting_flights, cancelled_flight)
    
    assert priority == PriorityLevel.HIGH
    assert "Imminent connecting flight" in reason
    assert "20:30" in reason


def test_medium_connection_priority():
    """Case 3: Connection > 4 hours but ≤ 18 hours - MEDIUM priority."""
    # Setup: Cancelled flight at 6:00 PM, connecting flight at 11:00 PM (5 hours)
    cancelled_departure = datetime(2024, 1, 15, 18, 0, 0, tzinfo=timezone.utc)
    connecting_departure = datetime(2024, 1, 15, 23, 0, 0, tzinfo=timezone.utc)
    
    passenger = MockPassenger(special_requirement=None)
    connecting_flights = [MockConnectingFlight(departure_time=connecting_departure)]
    cancelled_flight = MockCancelledFlight(departure_time=cancelled_departure)
    
    priority, reason = score_priority(passenger, connecting_flights, cancelled_flight)
    
    assert priority == PriorityLevel.MEDIUM
    assert "later the same day" in reason or "next morning" in reason


def test_normal_connection_priority():
    """Case 4: Connection > 18 hours - NORMAL priority."""
    # Setup: Cancelled flight at 6:00 PM, connecting flight next day at 3:00 PM (21 hours)
    cancelled_departure = datetime(2024, 1, 15, 18, 0, 0, tzinfo=timezone.utc)
    connecting_departure = datetime(2024, 1, 16, 15, 0, 0, tzinfo=timezone.utc)
    
    passenger = MockPassenger(special_requirement=None)
    connecting_flights = [MockConnectingFlight(departure_time=connecting_departure)]
    cancelled_flight = MockCancelledFlight(departure_time=cancelled_departure)
    
    priority, reason = score_priority(passenger, connecting_flights, cancelled_flight)
    
    assert priority == PriorityLevel.NORMAL
    assert "ample buffer" in reason


def test_no_requirement_no_connection_normal_priority():
    """Case 5: No special requirement and no connecting flight - NORMAL priority."""
    passenger = MockPassenger(special_requirement=None)
    connecting_flights = []
    cancelled_flight = MockCancelledFlight(departure_time=datetime.now(timezone.utc))
    
    priority, reason = score_priority(passenger, connecting_flights, cancelled_flight)
    
    assert priority == PriorityLevel.NORMAL
    assert "No urgent requirement" in reason


def test_configurable_thresholds():
    """Test that thresholds use the configurable constants."""
    # Verify the constants are accessible and have expected values
    assert HIGH_CONNECTION_THRESHOLD_HOURS == 4
    assert MEDIUM_CONNECTION_THRESHOLD_HOURS == 18


def test_4_hour_threshold_boundary():
    """Test the 4-hour threshold boundary exactly."""
    cancelled_departure = datetime(2024, 1, 15, 18, 0, 0, tzinfo=timezone.utc)
    # Exactly 4 hours later
    connecting_departure = datetime(2024, 1, 15, 22, 0, 0, tzinfo=timezone.utc)
    
    passenger = MockPassenger(special_requirement=None)
    connecting_flights = [MockConnectingFlight(departure_time=connecting_departure)]
    cancelled_flight = MockCancelledFlight(departure_time=cancelled_departure)
    
    priority, reason = score_priority(passenger, connecting_flights, cancelled_flight)
    
    # Exactly 4 hours should be HIGH (≤ 4 hours)
    assert priority == PriorityLevel.HIGH


def test_18_hour_threshold_boundary():
    """Test the 18-hour threshold boundary exactly."""
    cancelled_departure = datetime(2024, 1, 15, 18, 0, 0, tzinfo=timezone.utc)
    # Exactly 18 hours later
    connecting_departure = datetime(2024, 1, 16, 12, 0, 0, tzinfo=timezone.utc)
    
    passenger = MockPassenger(special_requirement=None)
    connecting_flights = [MockConnectingFlight(departure_time=connecting_departure)]
    cancelled_flight = MockCancelledFlight(departure_time=cancelled_departure)
    
    priority, reason = score_priority(passenger, connecting_flights, cancelled_flight)
    
    # Exactly 18 hours should be MEDIUM (≤ 18 hours)
    assert priority == PriorityLevel.MEDIUM