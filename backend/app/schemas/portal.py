"""
backend/app/schemas/portal.py

Pydantic schemas for the passenger portal API.
"""

from pydantic import BaseModel, Field


class PortalRequirementRequest(BaseModel):
    """Request schema for updating passenger requirement."""
    
    requirement_type: str = Field(..., description="Type of requirement")
    details: str = Field(..., description="Details of the requirement")


class PortalContextResponse(BaseModel):
    """Response schema for portal context."""
    
    passenger: dict
    flight: dict
    booking: dict | None = None
    recommendation: dict | None = None


class PortalRequirementUpdateResponse(BaseModel):
    """Response schema for requirement update."""
    
    success: bool
    passenger: dict
    recommendation: dict
    error: str | None = None