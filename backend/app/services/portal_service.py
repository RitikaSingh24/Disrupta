"""
backend/app/services/portal_service.py

Portal service layer for passenger access token management and requirement updates.

Responsibilities:
  - Validate access tokens
  - Generate portal context for passengers
  - Update passenger requirements
  - Mark tokens as used
  - Re-trigger rebooking analysis

Rules:
  - Uses existing SQLAlchemy models
  - Uses async database operations
  - No direct HTTP handling
  - Token security handled server-side
"""

import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.access_token import PassengerAccessToken
from app.models.booking import Booking
from app.models.enums import RecommendationStatus
from app.models.flight import Flight
from app.models.passenger import Passenger
from app.models.recommendation import RebookingRecommendation
from app.services.rebooking_service import analyze_passenger


async def generate_portal_tokens(
    flight_id: UUID,
    passenger_ids: list[UUID],
    db: AsyncSession
) -> list[str]:
    """
    Generate single-use access tokens for affected passengers.
    
    Args:
        flight_id: UUID of the cancelled flight
        passenger_ids: List of passenger UUIDs affected by the cancellation
        db: Async database session
        
    Returns:
        List of generated tokens
    """
    tokens = []
    expires_at = datetime.now(timezone.utc) + timedelta(hours=settings.PORTAL_TOKEN_EXPIRY_HOURS)
    
    for passenger_id in passenger_ids:
        token = secrets.token_urlsafe(32)
        
        access_token = PassengerAccessToken(
            token=token,
            passenger_id=passenger_id,
            flight_id=flight_id,
            expires_at=expires_at,
            used=False,
        )
        
        db.add(access_token)
        tokens.append(token)
    
    await db.commit()
    return tokens


async def validate_token(
    token: str,
    db: AsyncSession
) -> Optional[PassengerAccessToken]:
    """
    Validate a portal access token.
    
    Args:
        token: The access token string
        db: Async database session
        
    Returns:
        PassengerAccessToken if valid, None otherwise
    """
    stmt = select(PassengerAccessToken).where(PassengerAccessToken.token == token)
    result = await db.execute(stmt)
    access_token = result.scalar_one_or_none()
    
    if not access_token:
        return None
    
    # Check if token is expired
    if access_token.expires_at < datetime.now(timezone.utc):
        return None
    
    # Check if token is already used
    if access_token.used:
        return None
    
    return access_token


async def get_portal_context(
    token: str,
    db: AsyncSession
) -> Optional[dict]:
    """
    Get passenger portal context from a valid token.
    
    Args:
        token: The access token string
        db: Async database session
        
    Returns:
        Dictionary with passenger, flight, booking, and recommendation context
    """
    access_token = await validate_token(token, db)
    
    if not access_token:
        return None
    
    # Get passenger with eager loading
    stmt = select(Passenger).where(Passenger.passenger_id == access_token.passenger_id)
    result = await db.execute(stmt)
    passenger = result.scalar_one_or_none()
    
    if not passenger:
        return None
    
    # Get flight
    flight_stmt = select(Flight).where(Flight.flight_id == access_token.flight_id)
    flight_result = await db.execute(flight_stmt)
    flight = flight_result.scalar_one_or_none()
    
    if not flight:
        return None
    
    # Get booking for this passenger on this flight
    booking_stmt = select(Booking).where(
        Booking.passenger_id == passenger.passenger_id,
        Booking.flight_id == flight.flight_id
    )
    booking_result = await db.execute(booking_stmt)
    booking = booking_result.scalar_one_or_none()
    
    # Get existing recommendation
    recommendation = None
    if booking:
        rec_stmt = select(RebookingRecommendation).where(
            RebookingRecommendation.passenger_id == passenger.passenger_id,
            RebookingRecommendation.booking_id == booking.booking_id,
            RebookingRecommendation.original_flight_id == flight.flight_id
        )
        rec_result = await db.execute(rec_stmt)
        recommendation = rec_result.scalar_one_or_none()
    
    return {
        "passenger": {
            "passenger_id": str(passenger.passenger_id),
            "name": passenger.name,
            "email": passenger.email,
            "phone": passenger.phone,
            "preferred_language": passenger.preferred_language,
            "special_requirement": passenger.special_requirement,
            "requirement_type": passenger.requirement_type,
            "requirement_declared_at": passenger.requirement_declared_at.isoformat() if passenger.requirement_declared_at else None,
        },
        "flight": {
            "flight_id": str(flight.flight_id),
            "flight_number": flight.flight_number,
            "airline": flight.airline,
            "origin": flight.origin,
            "destination": flight.destination,
            "departure_time": flight.departure_time.isoformat(),
            "arrival_time": flight.arrival_time.isoformat(),
            "status": flight.status.value,
            "cancellation_reason": flight.cancellation_reason,
        },
        "booking": {
            "booking_id": str(booking.booking_id) if booking else None,
            "seat_number": booking.seat_number if booking else None,
            "booking_class": booking.booking_class if booking else None,
            "booking_status": booking.booking_status.value if booking else None,
        } if booking else None,
        "recommendation": {
            "recommendation_id": str(recommendation.recommendation_id) if recommendation else None,
            "priority": recommendation.priority.value if recommendation else None,
            "reason": recommendation.reason if recommendation else None,
            "status": recommendation.status.value if recommendation else None,
            "version": recommendation.version if recommendation else None,
        } if recommendation else None,
    }


async def update_passenger_requirement(
    token: str,
    requirement_type: str,
    details: str,
    db: AsyncSession
) -> Optional[dict]:
    """
    Update passenger special requirement and re-trigger rebooking analysis.
    
    Args:
        token: The access token string
        requirement_type: Type of requirement
        details: Details of the requirement
        db: Async database session
        
    Returns:
        Dictionary with updated passenger and recommendation context
    """
    access_token = await validate_token(token, db)
    
    if not access_token:
        return None
    
    # Get passenger
    stmt = select(Passenger).where(Passenger.passenger_id == access_token.passenger_id)
    result = await db.execute(stmt)
    passenger = result.scalar_one_or_none()
    
    if not passenger:
        return None
    
    # Get flight
    flight_stmt = select(Flight).where(Flight.flight_id == access_token.flight_id)
    flight_result = await db.execute(flight_stmt)
    flight = flight_result.scalar_one_or_none()
    
    if not flight:
        return None
    
    # Get booking
    booking_stmt = select(Booking).where(
        Booking.passenger_id == passenger.passenger_id,
        Booking.flight_id == flight.flight_id
    )
    booking_result = await db.execute(booking_stmt)
    booking = booking_result.scalar_one_or_none()
    
    if not booking:
        return None
    
    # Update passenger requirement
    passenger.special_requirement = details
    passenger.requirement_type = requirement_type
    passenger.requirement_declared_at = datetime.now(timezone.utc)
    passenger.updated_at = datetime.now(timezone.utc)
    
    # Find existing PENDING recommendation
    rec_stmt = select(RebookingRecommendation).where(
        RebookingRecommendation.passenger_id == passenger.passenger_id,
        RebookingRecommendation.booking_id == booking.booking_id,
        RebookingRecommendation.original_flight_id == flight.flight_id,
        RebookingRecommendation.status == RecommendationStatus.PENDING
    )
    rec_result = await db.execute(rec_stmt)
    recommendation = rec_result.scalar_one_or_none()
    
    # Re-run rebooking analysis
    try:
        updated_recommendation = await analyze_passenger(passenger.passenger_id, flight.flight_id, db)
    except Exception as e:
        # If analysis fails, still commit the requirement update
        await db.commit()
        return {
            "success": True,
            "error": f"Rebooking analysis failed: {str(e)}",
            "passenger": {
                "passenger_id": str(passenger.passenger_id),
                "special_requirement": passenger.special_requirement,
                "requirement_type": passenger.requirement_type,
            }
        }
    
    # Mark token as used
    access_token.used = True
    await db.commit()
    await db.refresh(updated_recommendation)
    
    return {
        "success": True,
        "passenger": {
            "passenger_id": str(passenger.passenger_id),
            "name": passenger.name,
            "special_requirement": passenger.special_requirement,
            "requirement_type": passenger.requirement_type,
        },
        "recommendation": {
            "recommendation_id": str(updated_recommendation.recommendation_id),
            "priority": updated_recommendation.priority.value,
            "reason": updated_recommendation.reason,
            "status": updated_recommendation.status.value,
            "version": updated_recommendation.version,
        }
    }