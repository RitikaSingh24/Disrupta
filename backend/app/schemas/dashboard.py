"""
backend/app/schemas/dashboard.py

Pydantic schemas for dashboard requests and responses.
"""

from pydantic import BaseModel, ConfigDict


class DashboardOverviewResponse(BaseModel):
    """Response schema for dashboard overview."""

    total_flights: int
    cancelled_flights: int
    affected_passengers: int
    pending_recommendations: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_flights": 50,
                "cancelled_flights": 3,
                "affected_passengers": 150,
                "pending_recommendations": 45,
            }
        }
    )