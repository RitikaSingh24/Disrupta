"""
tests/test_matching_engine.py

Tests for the pure alternative flight matching engine.

These tests focus on business logic and do NOT require:
- network
- OpenAI
- Supabase
- external APIs
- LLMs
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.services.matching_engine import (
    CONNECTION_BUFFER_MINUTES,
    find_alternative,
)


class MockAlternativeFlight:
    """Mock alternative flight object for testing."""
    def __init__(self, flight_number, departure_time, arrival_time, available_seats):
        self.alternative_flight_id = uuid4()
        self.flight_number = flight_number
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.available_seats = available_seats


class MockPassenger:
    """Mock passenger object for testing."""
    pass


class MockConnectingFlight:
    """Mock connecting flight object for testing."""
    def __init__(self, departure_time):
        self.departure_time = departure_time


def test_rahul_worked_example_selects_ai305():
    """
    Test the exact worked example from the PRD using Rahul's scenario.
    
    Setup:
    - Rahul has connecting flight at 8:30 PM
    - Candidate flights: AI-305, AI-410, AI-520
    - 90-minute connection buffer
    - AI-305 should be selected based on earliest departure that meets buffer
    """
    # Setup Rahul's connecting flight at 8:30 PM
    connecting_departure = datetime(2024, 1, 15, 20, 30, 0, tzinfo=timezone.utc)
    connecting_flights = [MockConnectingFlight(departure_time=connecting_departure)]
    
    # Setup candidate flights
    # AI-305: Departs 6:15 PM, Arrives 7:00 PM (before 8:30 PM - 90 min = 7:00 PM)
    # AI-410: Departs 6:30 PM, Arrives 7:15 PM (before 8:30 PM - 90 min = 7:00 PM)
    # AI-520: Departs 7:00 PM, Arrives 7:45 PM (before 8:30 PM - 90 min = 7:00 PM)
    ai305 = MockAlternativeFlight(
        flight_number="AI-305",
        departure_time=datetime(2024, 1, 15, 18, 15, 0, tzinfo=timezone.utc),
        arrival_time=datetime(2024, 1, 15, 19, 0, 0, tzinfo=timezone.utc),
        available_seats=5
    )
    ai410 = MockAlternativeFlight(
        flight_number="AI-410",
        departure_time=datetime(2024, 1, 15, 18, 30, 0, tzinfo=timezone.utc),
        arrival_time=datetime(2024, 1, 15, 19, 15, 0, tzinfo=timezone.utc),
        available_seats=3
    )
    ai520 = MockAlternativeFlight(
        flight_number="AI-520",
        departure_time=datetime(2024, 1, 15, 19, 0, 0, tzinfo=timezone.utc),
        arrival_time=datetime(2024, 1, 15, 19, 45, 0, tzinfo=timezone.utc),
        available_seats=2
    )
    
    candidates = [ai305, ai410, ai520]
    passenger = MockPassenger()
    
    result = find_alternative(passenger, connecting_flights, candidates)
    
    # AI-305 should be selected (earliest departure that meets buffer)
    assert result is not None
    assert result.flight_number == "AI-305"


def test_no_available_seats_filtered():
    """Test that candidates with no available seats are filtered out."""
    connecting_departure = datetime(2024, 1, 15, 20, 30, 0, tzinfo=timezone.utc)
    connecting_flights = [MockConnectingFlight(departure_time=connecting_departure)]
    
    # All candidates have 0 available seats
    candidate1 = MockAlternativeFlight(
        flight_number="AI-100",
        departure_time=datetime(2024, 1, 15, 18, 0, 0, tzinfo=timezone.utc),
        arrival_time=datetime(2024, 1, 15, 19, 0, 0, tzinfo=timezone.utc),
        available_seats=0
    )
    candidate2 = MockAlternativeFlight(
        flight_number="AI-200",
        departure_time=datetime(2024, 1, 15, 19, 0, 0, tzinfo=timezone.utc),
        arrival_time=datetime(2024, 1, 15, 20, 0, 0, tzinfo=timezone.utc),
        available_seats=0
    )
    
    candidates = [candidate1, candidate2]
    passenger = MockPassenger()
    
    result = find_alternative(passenger, connecting_flights, candidates)
    
    assert result is None


def test_candidate_sorting_by_departure():
    """Test that candidates are sorted by departure time (earliest first)."""
    connecting_flights = []
    
    # Candidates in random order
    candidate1 = MockAlternativeFlight(
        flight_number="AI-300",
        departure_time=datetime(2024, 1, 15, 19, 0, 0, tzinfo=timezone.utc),
        arrival_time=datetime(2024, 1, 15, 20, 0, 0, tzinfo=timezone.utc),
        available_seats=5
    )
    candidate2 = MockAlternativeFlight(
        flight_number="AI-200",
        departure_time=datetime(2024, 1, 15, 18, 0, 0, tzinfo=timezone.utc),
        arrival_time=datetime(2024, 1, 15, 19, 0, 0, tzinfo=timezone.utc),
        available_seats=3
    )
    candidate3 = MockAlternativeFlight(
        flight_number="AI-400",
        departure_time=datetime(2024, 1, 15, 20, 0, 0, tzinfo=timezone.utc),
        arrival_time=datetime(2024, 1, 15, 21, 0, 0, tzinfo=timezone.utc),
        available_seats=2
    )
    
    candidates = [candidate1, candidate2, candidate3]
    passenger = MockPassenger()
    
    result = find_alternative(passenger, connecting_flights, candidates)
    
    # AI-200 (earliest departure) should be selected
    assert result is not None
    assert result.flight_number == "AI-200"


def test_connection_constraint_violation():
    """Test that candidates violating connection buffer are not selected."""
    # Connecting flight at 8:30 PM
    connecting_departure = datetime(2024, 1, 15, 20, 30, 0, tzinfo=timezone.utc)
    connecting_flights = [MockConnectingFlight(departure_time=connecting_departure)]
    
    # Candidate arrives at 7:45 PM (8:30 PM - 90 min = 7:00 PM deadline)
    # This candidate arrives at 7:45 PM, which is AFTER 7:00 PM, so not viable
    candidate = MockAlternativeFlight(
        flight_number="AI-600",
        departure_time=datetime(2024, 1, 15, 18, 30, 0, tzinfo=timezone.utc),
        arrival_time=datetime(2024, 1, 15, 19, 45, 0, tzinfo=timezone.utc),
        available_seats=5
    )
    
    candidates = [candidate]
    passenger = MockPassenger()
    
    result = find_alternative(passenger, connecting_flights, candidates)
    
    # Should return None because arrival time violates buffer
    assert result is None


def test_no_connecting_flight_earliest_available():
    """Test that with no connecting flight, earliest available candidate is returned."""
    connecting_flights = []
    
    candidate1 = MockAlternativeFlight(
        flight_number="AI-100",
        departure_time=datetime(2024, 1, 15, 19, 0, 0, tzinfo=timezone.utc),
        arrival_time=datetime(2024, 1, 15, 20, 0, 0, tzinfo=timezone.utc),
        available_seats=5
    )
    candidate2 = MockAlternativeFlight(
        flight_number="AI-200",
        departure_time=datetime(2024, 1, 15, 18, 0, 0, tzinfo=timezone.utc),
        arrival_time=datetime(2024, 1, 15, 19, 0, 0, tzinfo=timezone.utc),
        available_seats=3
    )
    
    candidates = [candidate1, candidate2]
    passenger = MockPassenger()
    
    result = find_alternative(passenger, connecting_flights, candidates)
    
    # AI-200 (earliest departure) should be selected
    assert result is not None
    assert result.flight_number == "AI-200"


def test_empty_candidates_returns_none():
    """Test that empty candidates list returns None."""
    connecting_flights = []
    candidates = []
    passenger = MockPassenger()
    
    result = find_alternative(passenger, connecting_flights, candidates)
    
    assert result is None


def test_configurable_buffer_constant():
    """Test that the connection buffer uses the configurable constant."""
    assert CONNECTION_BUFFER_MINUTES == 90


def test_90_minute_buffer_exact_boundary():
    """Test the 90-minute buffer boundary exactly."""
    # Connecting flight at 8:30 PM
    connecting_departure = datetime(2024, 1, 15, 20, 30, 0, tzinfo=timezone.utc)
    connecting_flights = [MockConnectingFlight(departure_time=connecting_departure)]
    
    # Candidate arrives exactly at 7:00 PM (8:30 PM - 90 min = 7:00 PM)
    candidate = MockAlternativeFlight(
        flight_number="AI-100",
        departure_time=datetime(2024, 1, 15, 18, 0, 0, tzinfo=timezone.utc),
        arrival_time=datetime(2024, 1, 15, 19, 0, 0, tzinfo=timezone.utc),
        available_seats=5
    )
    
    candidates = [candidate]
    passenger = MockPassenger()
    
    result = find_alternative(passenger, connecting_flights, candidates)
    
    # Should be viable (arrives exactly at deadline)
    assert result is not None
    assert result.flight_number == "AI-100"
