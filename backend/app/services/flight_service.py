"""
backend/app/services/flight_service.py

Flight service layer for business logic related to flights and affected passengers.

Responsibilities:
  - Retrieve passengers affected by a particular flight
  - Calculate passenger counts for flights
  - Retrieve connecting flights for passengers
  - Provide data needed for future rebooking engine

Rules:
  - Uses existing SQLAlchemy models
  - Uses async database operations
  - No direct HTTP handling
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.booking import Booking
from app.models.connecting_flight import ConnectingFlight
from app.models.flight import Flight
from app.models.passenger import Passenger


async def get_affected_passengers(
    flight_id: UUID,
    db: AsyncSession
) -> list[dict]:
    """
    Retrieve passengers affected by a particular flight.
    
    This identifies passengers whose booking belongs to the supplied flight
    and provides information required by the future rebooking engine:
    - passenger ID
    - passenger name
    - contact information
    - special requirement
    - booking information relevant to the affected flight
    - connecting-flight information
    
    Args:
        flight_id: UUID of the flight to check
        db: Async database session
        
    Returns:
        List of dictionaries containing passenger and booking information
        
    Raises:
        ValueError: If flight does not exist
    """
    # First verify the flight exists
    flight_stmt = select(Flight).where(Flight.flight_id == flight_id)
    flight_result = await db.execute(flight_stmt)
    flight = flight_result.scalar_one_or_none()
    
    if not flight:
        raise ValueError(f"Flight with ID {flight_id} not found")
    
    # Query bookings for this flight and eagerly load passenger and connecting flight data
    stmt = (
        select(Booking)
        .where(Booking.flight_id == flight_id)
        .options(
            selectinload(Booking.passenger),
            selectinload(Booking.connecting_flights)
        )
    )
    
    result = await db.execute(stmt)
    bookings = result.scalars().all()
    
    affected_passengers = []
    
    for booking in bookings:
        passenger = booking.passenger
        
        # Get connecting flights for this passenger
        connecting_flights = await get_connecting_flights(passenger.passenger_id, db)
        
        passenger_data = {
            "passenger_id": str(passenger.passenger_id),
            "name": passenger.name,
            "email": passenger.email,
            "phone": passenger.phone,
            "preferred_language": passenger.preferred_language,
            "special_requirement": passenger.special_requirement,
            "requirement_type": passenger.requirement_type,
            "requirement_declared_at": passenger.requirement_declared_at.isoformat() if passenger.requirement_declared_at else None,
            "booking": {
                "booking_id": str(booking.booking_id),
                "flight_id": str(booking.flight_id),
                "seat_number": booking.seat_number,
                "booking_class": booking.booking_class,
                "booking_status": booking.booking_status.value,
                "created_at": booking.created_at.isoformat(),
            },
            "connecting_flights": [
                {
                    "connection_id": str(cf.connection_id),
                    "flight_number": cf.flight_number,
                    "departure_time": cf.departure_time.isoformat(),
                    "destination": cf.destination,
                    "created_at": cf.created_at.isoformat(),
                }
                for cf in connecting_flights
            ]
        }
        
        affected_passengers.append(passenger_data)
    
    return affected_passengers


async def get_connecting_flights(
    passenger_id: UUID,
    db: AsyncSession
) -> list[ConnectingFlight]:
    """
    Retrieve connecting flights for a passenger.
    
    Args:
        passenger_id: UUID of the passenger
        db: Async database session
        
    Returns:
        List of ConnectingFlight ORM objects
    """
    stmt = select(ConnectingFlight).where(ConnectingFlight.passenger_id == passenger_id)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_flight_passenger_count(
    flight_id: UUID,
    db: AsyncSession
) -> int:
    """
    Calculate the number of passengers associated with a flight.
    
    Args:
        flight_id: UUID of the flight
        db: Async database session
        
    Returns:
        Number of passengers booked on this flight
        
    Raises:
        ValueError: If flight does not exist
    """
    # First verify the flight exists
    flight_stmt = select(Flight).where(Flight.flight_id == flight_id)
    flight_result = await db.execute(flight_stmt)
    flight = flight_result.scalar_one_or_none()
    
    if not flight:
        raise ValueError(f"Flight with ID {flight_id} not found")
    
    # Count distinct passengers for this flight
    stmt = select(Booking.passenger_id).where(Booking.flight_id == flight_id).distinct()
    result = await db.execute(stmt)
    passenger_ids = result.scalars().all()
    
    return len(passenger_ids)