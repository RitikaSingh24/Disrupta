"""
backend/app/services/passenger_service.py

Passenger service layer for passenger-related operations.

Responsibilities:
  - Retrieve passenger information
  - Retrieve passenger with related data

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

from app.models.passenger import Passenger


async def get_passenger(
    passenger_id: UUID,
    db: AsyncSession
) -> Optional[Passenger]:
    """
    Retrieve a passenger by ID with related data.
    
    Args:
        passenger_id: UUID of the passenger
        db: Async database session
        
    Returns:
        Passenger ORM object with bookings and connecting flights loaded, or None if not found
    """
    stmt = (
        select(Passenger)
        .where(Passenger.passenger_id == passenger_id)
        .options(
            selectinload(Passenger.bookings),
            selectinload(Passenger.connecting_flights)
        )
    )
    
    result = await db.execute(stmt)
    return result.scalar_one_or_none()