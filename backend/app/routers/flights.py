"""
backend/app/routers/flights.py

Flights Router.

Endpoints:
  - GET /flights: List flights with optional status filtering
  - GET /flights/{flight_id}: Get detailed flight information with passenger count
  - POST /flights/{flight_id}/cancel: Cancel a flight

Rules:
  - Requires JWT authentication via get_current_user
  - Uses existing Flight model
  - Uses existing async database session
  - Returns Pydantic response schemas
  - Handles 404 for nonexistent flights
"""

from typing import Optional
from uuid import UUID
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user
from app.db.session import get_db
from app.models.enums import FlightStatus
from app.models.flight import Flight
from app.models.user import User
from app.schemas.flight import (
    CancelFlightRequest,
    CancelFlightResponse,
    FlightDetailResponse,
    FlightListResponse,
    FlightResponse,
)
from app.services.flight_service import get_flight_passenger_count
from app.services.flight_service import get_affected_passengers
from app.services.portal_service import generate_portal_tokens

router = APIRouter(prefix="/flights", tags=["Flights"])
logger = logging.getLogger(__name__)


@router.get(
    "",
    response_model=FlightListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Flights",
    description="Retrieve a list of flights with optional filtering by status.",
)
async def list_flights(
    status: Optional[FlightStatus] = Query(None, description="Filter by flight status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FlightListResponse:
    """
    List all flights with optional status filtering.
    
    Requires JWT authentication.
    """
    stmt = select(Flight)
    
    if status:
        stmt = stmt.where(Flight.status == status)
    
    result = await db.execute(stmt)
    flights = result.scalars().all()
    
    flight_responses = [FlightResponse.model_validate(flight) for flight in flights]
    
    return FlightListResponse(
        flights=flight_responses,
        count=len(flight_responses)
    )


@router.get(
    "/{flight_id}",
    response_model=FlightDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Flight Details",
    description="Retrieve detailed information for a specific flight including passenger count.",
)
async def get_flight(
    flight_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FlightDetailResponse:
    """
    Get detailed flight information including passenger count.
    
    Requires JWT authentication.
    Returns 404 if flight does not exist.
    """
    # Get flight details
    stmt = select(Flight).where(Flight.flight_id == flight_id)
    result = await db.execute(stmt)
    flight = result.scalar_one_or_none()
    
    if not flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flight with ID {flight_id} not found"
        )
    
    # Calculate passenger count
    try:
        passenger_count = await get_flight_passenger_count(flight_id, db)
    except ValueError:
        # Flight doesn't exist (shouldn't happen since we checked above)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flight with ID {flight_id} not found"
        )
    
    return FlightDetailResponse(
        flight_id=flight.flight_id,
        flight_number=flight.flight_number,
        airline=flight.airline,
        origin=flight.origin,
        destination=flight.destination,
        departure_time=flight.departure_time,
        arrival_time=flight.arrival_time,
        status=flight.status,
        cancellation_reason=flight.cancellation_reason,
        total_seats=flight.total_seats,
        passenger_count=passenger_count,
        created_at=flight.created_at,
        updated_at=flight.updated_at,
    )


@router.post(
    "/{flight_id}/cancel",
    response_model=CancelFlightResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancel Flight",
    description="Cancel a flight by changing its status to CANCELLED.",
)
async def cancel_flight(
    flight_id: UUID,
    payload: CancelFlightRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CancelFlightResponse:
    """
    Cancel a flight by changing its status to CANCELLED.
    
    Requires JWT authentication.
    Returns 404 if flight does not exist.
    The cancellation reason is accepted in the request but only persisted
    if the existing schema supports it (cancellation_reason field exists).
    """
    # Get flight
    stmt = select(Flight).where(Flight.flight_id == flight_id)
    result = await db.execute(stmt)
    flight = result.scalar_one_or_none()
    
    if not flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flight with ID {flight_id} not found"
        )
    
    # Update flight status to CANCELLED
    flight.status = FlightStatus.CANCELLED
    
    # Only persist cancellation_reason if the field exists in the model
    # (it does exist in the current schema)
    flight.cancellation_reason = payload.reason
    
    # Update timestamp
    from datetime import datetime, timezone
    flight.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(flight)
    
    # Generate portal access tokens for affected passengers
    try:
        affected_passengers = await get_affected_passengers(flight_id, db)
        passenger_ids = [UUID(p["passenger_id"]) for p in affected_passengers]
        tokens = await generate_portal_tokens(flight_id, passenger_ids, db)
    except Exception as e:
        # Log warning but don't fail the cancellation if token generation fails
        # Token generation is a convenience feature, not critical to cancellation
        logger.warning(f"Failed to generate portal tokens: {e}")
    
    # Trigger rebooking analysis for affected passengers
    try:
        from app.services.rebooking_service import analyze_passenger
        affected_passengers = await get_affected_passengers(flight_id, db)
        for passenger_data in affected_passengers:
            passenger_id = UUID(passenger_data["passenger_id"])
            try:
                await analyze_passenger(passenger_id, flight_id, db)
            except ValueError as e:
                # Skip if booking not found or other data issue
                logger.warning(f"Failed to analyze passenger {passenger_id}: {e}")
                continue
    except Exception as e:
        # Log warning but don't fail the cancellation if analysis fails
        # Rebooking analysis is a background process, not critical to cancellation
        logger.warning(f"Failed to trigger rebooking analysis: {e}")
    
    return CancelFlightResponse(
        flight_id=flight.flight_id,
        flight_number=flight.flight_number,
        airline=flight.airline,
        origin=flight.origin,
        destination=flight.destination,
        departure_time=flight.departure_time,
        arrival_time=flight.arrival_time,
        status=flight.status,
        cancellation_reason=flight.cancellation_reason,
        total_seats=flight.total_seats,
        created_at=flight.created_at,
        updated_at=flight.updated_at,
    )