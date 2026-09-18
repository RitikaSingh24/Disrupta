"""
backend/app/agent/tools.py

Thin async wrappers around existing service functions for the AI reasoning layer.
"""

from uuid import UUID
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.booking_service import (
    get_booking,
    get_booking_by_passenger_and_flight,
    get_available_flights,
    update_rebooking,
)
from app.services.passenger_service import get_passenger
from app.services.flight_service import get_connecting_flights


async def tool_get_passenger(
    passenger_id: UUID,
    db: AsyncSession
) -> Optional[dict]:
    """
    Wrapper for passenger service.
    
    Returns passenger data as dict for agent consumption.
    """
    passenger = await get_passenger(passenger_id, db)
    if not passenger:
        return None
    
    return {
        "passenger_id": str(passenger.passenger_id),
        "name": passenger.name,
        "email": passenger.email,
        "phone": passenger.phone,
        "preferred_language": passenger.preferred_language,
        "special_requirement": passenger.special_requirement,
        "requirement_type": passenger.requirement_type,
        "requirement_declared_at": passenger.requirement_declared_at.isoformat() if passenger.requirement_declared_at else None,
    }


async def tool_get_booking(
    booking_id: UUID,
    db: AsyncSession
) -> Optional[dict]:
    """
    Wrapper for booking service.
    
    Returns booking data as dict for agent consumption.
    """
    booking = await get_booking(booking_id, db)
    if not booking:
        return None
    
    return {
        "booking_id": str(booking.booking_id),
        "passenger_id": str(booking.passenger_id),
        "flight_id": str(booking.flight_id),
        "seat_number": booking.seat_number,
        "booking_class": booking.booking_class,
        "booking_status": booking.booking_status.value,
        "rebooked_flight_id": str(booking.rebooked_flight_id) if booking.rebooked_flight_id else None,
    }


async def tool_get_booking_by_passenger_and_flight(
    passenger_id: UUID,
    flight_id: UUID,
    db: AsyncSession
) -> Optional[dict]:
    """
    Wrapper for booking service by passenger and flight.
    """
    booking = await get_booking_by_passenger_and_flight(passenger_id, flight_id, db)
    if not booking:
        return None
    
    return {
        "booking_id": str(booking.booking_id),
        "passenger_id": str(booking.passenger_id),
        "flight_id": str(booking.flight_id),
        "seat_number": booking.seat_number,
        "booking_class": booking.booking_class,
        "booking_status": booking.booking_status.value,
    }


async def tool_get_connecting_flights(
    passenger_id: UUID,
    db: AsyncSession
) -> list[dict]:
    """
    Wrapper for connecting flights service.
    
    Returns connecting flights as list of dicts for agent consumption.
    """
    connecting_flights = await get_connecting_flights(passenger_id, db)
    
    return [
        {
            "connection_id": str(cf.connection_id),
            "flight_number": cf.flight_number,
            "departure_time": cf.departure_time.isoformat(),
            "destination": cf.destination,
        }
        for cf in connecting_flights
    ]


async def tool_get_available_flights(
    origin: str,
    destination: str,
    db: AsyncSession
) -> list[dict]:
    """
    Wrapper for available flights service.
    
    Returns available alternative flights as list of dicts for agent consumption.
    """
    flights = await get_available_flights(origin, destination, db)
    
    return [
        {
            "alternative_flight_id": str(f.alternative_flight_id),
            "flight_number": f.flight_number,
            "airline": f.airline,
            "origin": f.origin,
            "destination": f.destination,
            "departure_time": f.departure_time.isoformat(),
            "arrival_time": f.arrival_time.isoformat(),
            "available_seats": f.available_seats,
        }
        for f in flights
    ]


async def tool_update_rebooking(
    booking_id: UUID,
    recommended_flight_id: UUID,
    db: AsyncSession
) -> dict:
    """
    Wrapper for rebooking update service.
    
    Returns updated booking data as dict.
    """
    booking = await update_rebooking(booking_id, recommended_flight_id, db)
    
    return {
        "booking_id": str(booking.booking_id),
        "rebooked_flight_id": str(booking.rebooked_flight_id) if booking.rebooked_flight_id else None,
    }