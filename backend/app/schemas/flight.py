"""
backend/app/schemas/flight.py

Pydantic v2 schemas for flight-related requests and responses.

Rules:
  - Only contains schemas required for flight API endpoints.
  - No database models or logic.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import FlightStatus


class FlightResponse(BaseModel):
    """Response schema for flight information."""

    flight_id: UUID = Field(..., description="Unique flight identifier")
    flight_number: str = Field(..., description="Flight number (e.g., AA-100)")
    airline: str = Field(..., description="Airline name")
    origin: str = Field(..., description="Origin airport code")
    destination: str = Field(..., description="Destination airport code")
    departure_time: datetime = Field(..., description="Scheduled departure time")
    arrival_time: datetime = Field(..., description="Scheduled arrival time")
    status: FlightStatus = Field(..., description="Current flight status")
    cancellation_reason: Optional[str] = Field(None, description="Reason for cancellation if applicable")
    total_seats: int = Field(..., description="Total seats on the aircraft")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Record last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class FlightListResponse(BaseModel):
    """Response schema for flight list endpoint."""

    flights: list[FlightResponse] = Field(..., description="List of flights")
    count: int = Field(..., description="Total number of flights returned")


class FlightDetailResponse(BaseModel):
    """Response schema for detailed flight information including passenger count."""

    flight_id: UUID = Field(..., description="Unique flight identifier")
    flight_number: str = Field(..., description="Flight number (e.g., AA-100)")
    airline: str = Field(..., description="Airline name")
    origin: str = Field(..., description="Origin airport code")
    destination: str = Field(..., description="Destination airport code")
    departure_time: datetime = Field(..., description="Scheduled departure time")
    arrival_time: datetime = Field(..., description="Scheduled arrival time")
    status: FlightStatus = Field(..., description="Current flight status")
    cancellation_reason: Optional[str] = Field(None, description="Reason for cancellation if applicable")
    total_seats: int = Field(..., description="Total seats on the aircraft")
    passenger_count: int = Field(..., description="Number of passengers booked on this flight")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Record last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class CancelFlightRequest(BaseModel):
    """Request schema for flight cancellation."""

    reason: str = Field(..., min_length=1, description="Reason for flight cancellation")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "reason": "Aircraft maintenance issue"
            }
        }
    )


class CancelFlightResponse(BaseModel):
    """Response schema for flight cancellation."""

    flight_id: UUID = Field(..., description="Unique flight identifier")
    flight_number: str = Field(..., description="Flight number (e.g., AA-100)")
    airline: str = Field(..., description="Airline name")
    origin: str = Field(..., description="Origin airport code")
    destination: str = Field(..., description="Destination airport code")
    departure_time: datetime = Field(..., description="Scheduled departure time")
    arrival_time: datetime = Field(..., description="Scheduled arrival time")
    status: FlightStatus = Field(..., description="Updated flight status (CANCELLED)")
    cancellation_reason: Optional[str] = Field(None, description="Reason for cancellation if persisted")
    total_seats: int = Field(..., description="Total seats on the aircraft")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Record last update timestamp")

    model_config = ConfigDict(from_attributes=True)