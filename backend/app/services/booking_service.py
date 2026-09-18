"""
backend/app/services/booking_service.py

Booking service layer for booking-related operations.

Responsibilities:
  - Retrieve booking information
  - Retrieve available alternative flights
  - Update booking rebooking information

Rules:
  - Uses existing SQLAlchemy models
  - Uses async database operations
  - No direct HTTP handling
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alternative_flight import AlternativeFlight
from app.models.booking import Booking


async def get_booking(
    booking_id: UUID,
    db: AsyncSession
) -> Optional[Booking]:
    """
    Retrieve a booking by ID.
    
    Args:
        booking_id: UUID of the booking
        db: Async database session
        
    Returns:
        Booking ORM object or None if not found
    """
    stmt = select(Booking).where(Booking.booking_id == booking_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_booking_by_passenger_and_flight(
    passenger_id: UUID,
    flight_id: UUID,
    db: AsyncSession
) -> Optional[Booking]:
    """
    Retrieve a booking by passenger ID and flight ID.
    
    Args:
        passenger_id: UUID of the passenger
        flight_id: UUID of the flight
        db: Async database session
        
    Returns:
        Booking ORM object or None if not found
    """
    stmt = select(Booking).where(
        Booking.passenger_id == passenger_id,
        Booking.flight_id == flight_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_available_flights(
    origin: str,
    destination: str,
    db: AsyncSession
) -> list[AlternativeFlight]:
    """
    Retrieve available alternative flights for a given route.
    
    Args:
        origin: Origin airport code
        destination: Destination airport code
        db: Async database session
        
    Returns:
        List of AlternativeFlight ORM objects
    """
    stmt = select(AlternativeFlight).where(
        AlternativeFlight.origin == origin,
        AlternativeFlight.destination == destination
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def update_rebooking(
    booking_id: UUID,
    recommended_flight_id: UUID,
    db: AsyncSession
) -> Booking:
    """
    Update a booking's rebooked flight.
    
    Args:
        booking_id: UUID of the booking to update
        recommended_flight_id: UUID of the new flight to rebook to
        db: Async database session
        
    Returns:
        Updated Booking ORM object
        
    Raises:
        ValueError: If booking not found
    """
    booking = await get_booking(booking_id, db)
    
    if not booking:
        raise ValueError(f"Booking with ID {booking_id} not found")
    
    booking.rebooked_flight_id = recommended_flight_id
    await db.commit()
    await db.refresh(booking)
    
    return booking