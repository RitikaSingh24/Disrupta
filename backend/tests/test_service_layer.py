"""
tests/test_service_layer.py

Tests for the extracted service layer functions.

These tests verify that the service functions exist and have the correct signatures.
They do not require database connection for basic structure verification.
"""

from uuid import uuid4

import pytest

from app.services.booking_service import get_booking, get_booking_by_passenger_and_flight, get_available_flights, update_rebooking
from app.services.passenger_service import get_passenger
from app.services.flight_service import get_connecting_flights


def test_booking_service_functions_exist():
    """Test that booking service functions are defined and callable."""
    # These functions are async and require db, but we can verify they exist
    assert callable(get_booking)
    assert callable(get_booking_by_passenger_and_flight)
    assert callable(get_available_flights)
    assert callable(update_rebooking)


def test_passenger_service_function_exists():
    """Test that passenger service function is defined and callable."""
    assert callable(get_passenger)


def test_connecting_flights_function_exists():
    """Test that connecting flights service function is defined and callable."""
    assert callable(get_connecting_flights)


def test_service_functions_signature():
    """Test that service functions have expected parameter names."""
    import inspect
    
    # Check get_booking signature
    sig = inspect.signature(get_booking)
    params = list(sig.parameters.keys())
    assert 'booking_id' in params
    assert 'db' in params
    
    # Check get_passenger signature
    sig = inspect.signature(get_passenger)
    params = list(sig.parameters.keys())
    assert 'passenger_id' in params
    assert 'db' in params
    
    # Check get_connecting_flights signature
    sig = inspect.signature(get_connecting_flights)
    params = list(sig.parameters.keys())
    assert 'passenger_id' in params
    assert 'db' in params
    
    # Check get_available_flights signature
    sig = inspect.signature(get_available_flights)
    params = list(sig.parameters.keys())
    assert 'origin' in params
    assert 'destination' in params
    assert 'db' in params
    
    # Check update_rebooking signature
    sig = inspect.signature(update_rebooking)
    params = list(sig.parameters.keys())
    assert 'booking_id' in params
    assert 'recommended_flight_id' in params
    assert 'db' in params