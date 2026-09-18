"""
backend/app/schemas/notification.py

Pydantic v2 schemas for notification API requests and responses.

Rules:
  - Only contains schemas required for notification API endpoints.
  - No database models or logic.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import NotificationStatus


class NotificationResponse(BaseModel):
    """Response schema for a single notification."""

    notification_id: UUID = Field(..., description="Unique notification identifier")
    passenger_id: UUID = Field(..., description="ID of the passenger")
    recommendation_id: Optional[UUID] = Field(None, description="ID of the related recommendation")
    language: str = Field(..., description="Language of the notification")
    message: str = Field(..., description="Notification message body")
    status: NotificationStatus = Field(..., description="Notification status")
    created_at: datetime = Field(..., description="Notification creation timestamp")
    sent_at: Optional[datetime] = Field(None, description="Notification sent timestamp")

    model_config = ConfigDict(from_attributes=True)


class UpdateNotificationRequest(BaseModel):
    """Request schema for PATCH /api/v1/notifications/{notification_id}."""

    message: str = Field(..., min_length=1, description="Updated notification message")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Updated notification message"
            }
        }
    )