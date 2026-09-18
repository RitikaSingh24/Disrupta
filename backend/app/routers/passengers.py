"""
backend/app/routers/passengers.py

Passengers Router.

Endpoints:
  - GET /passengers/{passenger_id}: Get detailed passenger profile

Rules:
  - Requires JWT authentication via get_current_user
  - Uses existing Passenger model
  - Uses existing async database session
  - Returns Pydantic response schemas
  - Handles 404 for nonexistent passengers
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.passenger import (
    BookingResponse,
    ConnectingFlightResponse,
    PassengerDetailResponse,
)
from app.services.passenger_service import get_passenger

router = APIRouter(prefix="/passengers", tags=["Passengers"])


@router.get(
    "/{passenger_id}",
    response_model=PassengerDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Passenger Details",
    description="Retrieve detailed passenger profile including bookings and connecting flights.",
)
async def get_passenger(
    passenger_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PassengerDetailResponse:
    """
    Get detailed passenger profile with bookings and connecting flights.
    
    Requires JWT authentication.
    Returns 404 if passenger does not exist.
    """
    # Get passenger with bookings and connecting flights eagerly loaded
    passenger = await get_passenger(passenger_id, db)
    
    if not passenger:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Passenger with ID {passenger_id} not found"
        )
    
    # Convert bookings to response schemas
    booking_responses = [
        BookingResponse.model_validate(booking)
        for booking in passenger.bookings
    ]
    
    # Convert connecting flights to response schemas
    connecting_flight_responses = [
        ConnectingFlightResponse.model_validate(cf)
        for cf in passenger.connecting_flights
    ]
    
    return PassengerDetailResponse(
        passenger_id=passenger.passenger_id,
        name=passenger.name,
        email=passenger.email,
        phone=passenger.phone,
        preferred_language=passenger.preferred_language,
        special_requirement=passenger.special_requirement,
        requirement_type=passenger.requirement_type,
        requirement_declared_at=passenger.requirement_declared_at,
        created_at=passenger.created_at,
        updated_at=passenger.updated_at,
        bookings=booking_responses,
        connecting_flights=connecting_flight_responses,
    )