"""
backend/app/schemas/rebooking.py

Pydantic v2 schemas for rebooking API requests and responses.

Rules:
  - Only contains schemas required for rebooking API endpoints.
  - No database models or logic.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import PriorityLevel, RecommendationStatus


class AnalyzeRequest(BaseModel):
    """Request schema for POST /api/v1/rebooking/analyze."""

    flight_id: UUID = Field(..., description="ID of the cancelled flight to analyze")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "flight_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
    )


class RecommendationResponse(BaseModel):
    """Response schema for a single rebooking recommendation."""

    recommendation_id: UUID = Field(..., description="Unique recommendation identifier")
    passenger_id: UUID = Field(..., description="ID of the affected passenger")
    passenger_name: Optional[str] = Field(None, description="Name of the affected passenger")
    booking_id: UUID = Field(..., description="ID of the passenger's booking")
    original_flight_id: UUID = Field(..., description="ID of the cancelled flight")
    recommended_flight_id: Optional[UUID] = Field(None, description="ID of the recommended alternative flight")
    recommended_flight_number: Optional[str] = Field(None, description="Flight number of the recommended alternative flight")
    priority: PriorityLevel = Field(..., description="Calculated priority level")
    reason: str = Field(..., description="Explanation for the priority and recommendation")
    status: RecommendationStatus = Field(..., description="Recommendation status")
    version: int = Field(..., description="Recommendation version")
    created_at: datetime = Field(..., description="Recommendation creation timestamp")
    updated_at: datetime = Field(..., description="Recommendation last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class AnalyzeResponse(BaseModel):
    """Response schema for POST /api/v1/rebooking/analyze."""

    flight_id: UUID = Field(..., description="ID of the analyzed flight")
    recommendations: list[RecommendationResponse] = Field(..., description="List of recommendations for affected passengers")
    count: int = Field(..., description="Total number of recommendations generated")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "flight_id": "123e4567-e89b-12d3-a456-426614174000",
                "recommendations": [],
                "count": 0
            }
        }
    )


class EditRecommendationRequest(BaseModel):
    """Request schema for POST /api/v1/rebooking/{recommendation_id}/edit."""

    recommended_flight_id: UUID = Field(..., description="ID of the new recommended alternative flight")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "recommended_flight_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
    )