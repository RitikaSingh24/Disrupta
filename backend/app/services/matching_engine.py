"""
backend/app/services/matching_engine.py

Pure alternative flight matching engine for rebooking recommendations.

This module contains only pure business logic with no:
- DB calls
- SQLAlchemy queries
- HTTP requests
- FastAPI dependencies
- LLM calls
- filesystem operations
- global mutable state

Rules:
  - Zero LLM calls
  - Pure function that works only with passed data
  - Configurable connection buffer constant
"""

from datetime import timedelta
from typing import List, Optional

from app.models.alternative_flight import AlternativeFlight


# Configurable connection buffer (easily modifiable for demo preparation)
CONNECTION_BUFFER_MINUTES = 90


def find_alternative(
    passenger,
    connecting_flights,
    candidates: List[AlternativeFlight]
) -> Optional[AlternativeFlight]:
    """
    Find the best alternative flight for a passenger.
    
    This is a pure function that only operates on the data passed in.
    It does not access the database, make network calls, or use LLMs.
    
    Args:
        passenger: Passenger ORM object (not used in current logic but kept for future extensibility)
        connecting_flights: List of connecting flight objects with departure_time
        candidates: List of AlternativeFlight objects with available_seats, departure_time, arrival_time
        
    Returns:
        Best AlternativeFlight object or None if no suitable alternative exists
        
    Matching Logic:
    1. Filter out candidates with no available seats
    2. Sort candidates by departure time (earliest first)
    3. If passenger has connecting flights:
       - Find soonest connecting flight
       - Apply 90-minute connection buffer
       - Select earliest candidate that arrives 90 minutes before connection
    4. If no connecting flights:
       - Return earliest available candidate
    5. If no candidates available:
       - Return None
    """
    # Filter out candidates with no available seats
    available_candidates = [
        c for c in candidates
        if c.available_seats > 0
    ]
    
    # If no available candidates, return None
    if not available_candidates:
        return None
    
    # Sort by departure time (earliest first)
    available_candidates.sort(key=lambda c: c.departure_time)
    
    # If passenger has connecting flights, apply connection buffer constraint
    if connecting_flights:
        # Find the soonest connecting flight
        soonest_connection = min(cf.departure_time for cf in connecting_flights)
        
        # Calculate the latest acceptable arrival time
        buffer = timedelta(minutes=CONNECTION_BUFFER_MINUTES)
        latest_arrival = soonest_connection - buffer
        
        # Filter candidates that arrive before the deadline
        viable_candidates = [
            c for c in available_candidates
            if c.arrival_time <= latest_arrival
        ]
        
        # Return the earliest viable candidate, or None if none viable
        if viable_candidates:
            return viable_candidates[0]
        else:
            return None
    
    # No connecting flights - return earliest available candidate
    return available_candidates[0]