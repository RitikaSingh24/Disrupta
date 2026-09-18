"""
backend/app/schemas/passenger.py

Pydantic v2 schemas for passenger-related requests and responses.

Rules:
  - Only contains schemas required for passenger API endpoints.
  - No database models or logic.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ConnectingFlightResponse(BaseModel):
    """Response schema for connecting flight information."""

    connection_id: UUID = Field(..., description="Unique connecting flight identifier")
    flight_number: str = Field(..., description="Connecting flight number")
    departure_time: datetime = Field(..., description="Connecting flight departure time")
    destination: str = Field(..., description="Connecting flight destination")
    created_at: datetime = Field(..., description="Record creation timestamp")

    model_config = ConfigDict(from_attributes=True)


class BookingResponse(BaseModel):
    """Response schema for booking information."""

    booking_id: UUID = Field(..., description="Unique booking identifier")
    flight_id: UUID = Field(..., description="Associated flight ID")
    seat_number: Optional[str] = Field(None, description="Seat number if assigned")
    booking_class: str = Field(..., description="Booking class (Economy, Business, First)")
    booking_status: str = Field(..., description="Current booking status")
    created_at: datetime = Field(..., description="Record creation timestamp")

    model_config = ConfigDict(from_attributes=True)


class PassengerResponse(BaseModel):
    """Response schema for passenger profile information."""

    passenger_id: UUID = Field(..., description="Unique passenger identifier")
    name: str = Field(..., description="Passenger full name")
    email: str = Field(..., description="Passenger email address")
    phone: Optional[str] = Field(None, description="Passenger phone number")
    preferred_language: str = Field(..., description="Preferred language for communications")
    special_requirement: Optional[str] = Field(None, description="Special requirements or needs")
    requirement_type: Optional[str] = Field(None, description="Type of special requirement")
    requirement_declared_at: Optional[datetime] = Field(None, description="When requirement was declared")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Record last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class PassengerDetailResponse(BaseModel):
    """Response schema for detailed passenger profile including bookings and connecting flights."""

    passenger_id: UUID = Field(..., description="Unique passenger identifier")
    name: str = Field(..., description="Passenger full name")
    email: str = Field(..., description="Passenger email address")
    phone: Optional[str] = Field(None, description="Passenger phone number")
    preferred_language: str = Field(..., description="Preferred language for communications")
    special_requirement: Optional[str] = Field(None, description="Special requirements or needs")
    requirement_type: Optional[str] = Field(None, description="Type of special requirement")
    requirement_declared_at: Optional[datetime] = Field(None, description="When requirement was declared")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Record last update timestamp")
    bookings: list[BookingResponse] = Field(default_factory=list, description="Passenger's bookings")
    connecting_flights: list[ConnectingFlightResponse] = Field(default_factory=list, description="Passenger's connecting flights")

    model_config = ConfigDict(from_attributes=True)