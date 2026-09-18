"""
backend/app/services/dashboard_service.py

Dashboard service layer for overview statistics.

Responsibilities:
  - Calculate flight statistics
  - Calculate passenger statistics
  - Calculate recommendation statistics

Rules:
  - Uses existing SQLAlchemy models
  - Uses async database operations
  - No direct HTTP handling
"""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.flight import Flight
from app.models.booking import Booking
from app.models.recommendation import RebookingRecommendation
from app.models.enums import FlightStatus, RecommendationStatus


async def get_dashboard_overview(
    db: AsyncSession
) -> dict:
    """
    Get dashboard overview statistics.
    
    Args:
        db: Async database session
        
    Returns:
        Dictionary with overview statistics
    """
    # Total flights
    total_flights_stmt = select(func.count(Flight.flight_id))
    total_flights_result = await db.execute(total_flights_stmt)
    total_flights = total_flights_result.scalar() or 0
    
    # Cancelled flights
    cancelled_flights_stmt = select(func.count(Flight.flight_id)).where(
        Flight.status == FlightStatus.CANCELLED
    )
    cancelled_flights_result = await db.execute(cancelled_flights_stmt)
    cancelled_flights = cancelled_flights_result.scalar() or 0
    
    # Affected passengers (bookings on cancelled flights)
    affected_passengers_stmt = select(func.count(Booking.passenger_id)).join(
        Flight, Booking.flight_id == Flight.flight_id
    ).where(Flight.status == FlightStatus.CANCELLED)
    affected_passengers_result = await db.execute(affected_passengers_stmt)
    affected_passengers = affected_passengers_result.scalar() or 0
    
    # Pending recommendations
    pending_recommendations_stmt = select(func.count(RebookingRecommendation.recommendation_id)).where(
        RebookingRecommendation.status == RecommendationStatus.PENDING
    )
    pending_recommendations_result = await db.execute(pending_recommendations_stmt)
    pending_recommendations = pending_recommendations_result.scalar() or 0
    
    return {
        "total_flights": total_flights,
        "cancelled_flights": cancelled_flights,
        "affected_passengers": affected_passengers,
        "pending_recommendations": pending_recommendations,
    }