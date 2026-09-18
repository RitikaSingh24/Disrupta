"""
backend/app/services/rebooking_service.py

Rebooking service layer for orchestrating the rebooking analysis.

This service orchestrates database operations and calls the pure engines.
It does NOT contain priority/matching business logic - that's in the pure engines.

Responsibilities:
  - Fetch passenger, flight, connecting flights, alternative candidates
  - Call priority_engine and matching_engine
  - Apply escalation rule when no alternative found
  - Create/update recommendation in database
  - Manage transactions properly
  - Optionally integrate AI reasoning layer

Rules:
  - Reuses existing services (flight_service)
  - Reuses existing models
  - Uses existing async database session
  - No LLM calls when USE_AI_REASONING=False
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alternative_flight import AlternativeFlight
from app.models.booking import Booking
from app.models.enums import PriorityLevel, RecommendationStatus
from app.models.flight import Flight
from app.models.passenger import Passenger
from app.models.recommendation import RebookingRecommendation
from app.core.config import settings
from app.services.flight_service import get_affected_passengers, get_connecting_flights
from app.services.matching_engine import find_alternative
from app.services.priority_engine import score_priority

logger = logging.getLogger(__name__)


async def analyze_passenger(
    passenger_id: UUID,
    flight_id: UUID,
    db: AsyncSession
) -> RebookingRecommendation:
    """
    Analyze a single passenger for rebooking options.
    
    Orchestration flow:
    1. Fetch passenger, cancelled flight, connecting flights, alternative candidates
    2. Score priority using priority_engine
    3. Find alternative using matching_engine
    4. Apply escalation rule if no alternative found
    5. Create/update recommendation in database
    6. Return recommendation
    
    Args:
        passenger_id: UUID of the passenger to analyze
        flight_id: UUID of the cancelled flight
        db: Async database session
        
    Returns:
        RebookingRecommendation ORM object
        
    Raises:
        ValueError: If passenger or flight not found
    """
    # Fetch passenger
    passenger_stmt = select(Passenger).where(Passenger.passenger_id == passenger_id)
    passenger_result = await db.execute(passenger_stmt)
    passenger = passenger_result.scalar_one_or_none()
    
    if not passenger:
        raise ValueError(f"Passenger with ID {passenger_id} not found")
    
    # Fetch cancelled flight
    flight_stmt = select(Flight).where(Flight.flight_id == flight_id)
    flight_result = await db.execute(flight_stmt)
    flight = flight_result.scalar_one_or_none()
    
    if not flight:
        raise ValueError(f"Flight with ID {flight_id} not found")
    
    # Fetch connecting flights for this passenger
    connecting_flights = await get_connecting_flights(passenger_id, db)
    
    # Fetch alternative flight candidates
    # Get alternatives that match the route (origin -> destination)
    alt_flights_stmt = (
        select(AlternativeFlight)
        .where(
            AlternativeFlight.origin == flight.origin,
            AlternativeFlight.destination == flight.destination
        )
    )
    alt_flights_result = await db.execute(alt_flights_stmt)
    alternative_candidates = alt_flights_result.scalars().all()
    
    # Score priority using pure engine
    priority, reason = score_priority(passenger, connecting_flights, flight)
    
    # Find alternative using pure engine
    recommended_flight = find_alternative(passenger, connecting_flights, alternative_candidates)
    
    # Apply escalation rule: if no alternative found, force escalation
    if recommended_flight is None:
        status = RecommendationStatus.ESCALATED
        # Ensure priority is at least REVIEW_REQUIRED
        if priority == PriorityLevel.NORMAL:
            priority = PriorityLevel.REVIEW_REQUIRED
            reason = f"{reason} (escalated: no suitable alternative found)"
        else:
            reason = f"{reason} (escalated: no suitable alternative found)"
    else:
        status = RecommendationStatus.PENDING
    
    # AI Reasoning Layer integration (only if flag is enabled)
    if settings.USE_AI_REASONING:
        try:
            from app.agent.graph import run_ai_analysis
            ai_state = await run_ai_analysis(passenger_id, flight_id, db)
            
            if ai_state.get("error"):
                logger.warning(f"AI analysis failed: {ai_state['error']}, using deterministic result")
            else:
                # Use AI-generated reason if available (deterministic priority and flight remain unchanged)
                if ai_state.get("priority_reason"):
                    reason = ai_state["priority_reason"]
                
                # Notification data is available in ai_state for future use
                # (notification_en, notification_local, local_language)
                # This can be used when creating notifications
                
        except Exception as e:
            logger.warning(f"AI reasoning integration failed: {e}, using deterministic result")
    
    # Fetch booking for this passenger on this flight
    booking_stmt = (
        select(Booking)
        .where(
            Booking.passenger_id == passenger_id,
            Booking.flight_id == flight_id
        )
    )
    booking_result = await db.execute(booking_stmt)
    booking = booking_result.scalar_one_or_none()
    
    if not booking:
        raise ValueError(f"Booking not found for passenger {passenger_id} on flight {flight_id}")
    
    # Check if recommendation already exists for this passenger/booking/flight
    existing_rec_stmt = (
        select(RebookingRecommendation)
        .where(
            RebookingRecommendation.passenger_id == passenger_id,
            RebookingRecommendation.booking_id == booking.booking_id,
            RebookingRecommendation.original_flight_id == flight_id
        )
    )
    existing_rec_result = await db.execute(existing_rec_stmt)
    existing_rec = existing_rec_result.scalar_one_or_none()
    
    # Create or update recommendation
    if existing_rec:
        # Update existing recommendation
        existing_rec.priority = priority
        existing_rec.reason = reason
        existing_rec.status = status
        existing_rec.recommended_flight_id = recommended_flight.alternative_flight_id if recommended_flight else None
        existing_rec.version += 1
        existing_rec.updated_at = datetime.now(timezone.utc)
        
        await db.commit()
        await db.refresh(existing_rec)
        return existing_rec
    else:
        # Create new recommendation
        recommendation = RebookingRecommendation(
            passenger_id=passenger_id,
            booking_id=booking.booking_id,
            original_flight_id=flight_id,
            recommended_flight_id=recommended_flight.alternative_flight_id if recommended_flight else None,
            priority=priority,
            reason=reason,
            status=status,
            version=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        
        db.add(recommendation)
        await db.commit()
        await db.refresh(recommendation)
        return recommendation