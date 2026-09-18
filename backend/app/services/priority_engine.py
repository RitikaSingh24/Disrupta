"""
backend/app/services/priority_engine.py

Pure priority scoring engine for rebooking recommendations.

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
  - Configurable thresholds for connection time windows
"""

from datetime import timedelta
from typing import Tuple

from app.models.enums import PriorityLevel


# Configurable threshold constants (easily modifiable for demo preparation)
HIGH_CONNECTION_THRESHOLD_HOURS = 4
MEDIUM_CONNECTION_THRESHOLD_HOURS = 18


def score_priority(
    passenger,
    connecting_flights,
    cancelled_flight
) -> Tuple[PriorityLevel, str]:
    """
    Score passenger priority based on special requirements and connecting flights.
    
    This is a pure function that only operates on the data passed in.
    It does not access the database, make network calls, or use LLMs.
    
    Args:
        passenger: Passenger ORM object or dict with special_requirement field
        connecting_flights: List of connecting flight objects with departure_time
        cancelled_flight: Flight ORM object or dict with departure_time
        
    Returns:
        Tuple of (PriorityLevel, reason_string)
        
    Priority Logic:
    1. Special requirement → HIGH
    2. Connecting flight ≤ 4 hours → HIGH
    3. Connecting flight ≤ 18 hours → MEDIUM
    4. Connecting flight > 18 hours → NORMAL
    5. No special requirement + no connecting flight → NORMAL
    6. Insufficient data → REVIEW_REQUIRED
    """
    # Handle special requirement case
    if passenger.special_requirement is not None:
        requirement_text = passenger.special_requirement
        return PriorityLevel.HIGH, f"Passenger has declared: {requirement_text}"
    
    # Handle connecting flights
    if connecting_flights:
        # Find the soonest connecting flight
        soonest_connection = min(cf.departure_time for cf in connecting_flights)
        
        # Calculate time gap from cancelled flight departure
        gap = soonest_connection - cancelled_flight.departure_time
        gap_hours = gap.total_seconds() / 3600
        
        # High priority: imminent connection (≤ 4 hours)
        if gap_hours <= HIGH_CONNECTION_THRESHOLD_HOURS:
            return PriorityLevel.HIGH, f"Imminent connecting flight at {soonest_connection}"
        
        # Medium priority: same day or next morning connection (≤ 18 hours)
        elif gap_hours <= MEDIUM_CONNECTION_THRESHOLD_HOURS:
            return PriorityLevel.MEDIUM, "Connecting flight later the same day/next morning"
        
        # Normal priority: ample buffer (> 18 hours)
        else:
            return PriorityLevel.NORMAL, "Connecting flight has ample buffer"
    
    # No special requirement and no connecting flight
    if passenger.special_requirement is None and not connecting_flights:
        return PriorityLevel.NORMAL, "No urgent requirement found in available data"
    
    # Fallback for insufficient data
    return PriorityLevel.REVIEW_REQUIRED, "Insufficient data to determine priority"