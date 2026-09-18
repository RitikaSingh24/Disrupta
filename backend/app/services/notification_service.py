"""
backend/app/services/notification_service.py

Notification service for managing passenger notifications.

This service provides:
- Deterministic plain-text notification template generation
- Notification creation
- Notification retrieval
- Notification message update
- Simulated notification sending

Rules:
  - Zero AI
  - Zero external service calls
  - Zero email/SMS/WhatsApp
  - Uses existing Notification model
  - Uses existing NotificationStatus enum
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alternative_flight import AlternativeFlight
from app.models.enums import NotificationStatus
from app.models.flight import Flight
from app.models.notification import Notification
from app.models.passenger import Passenger
from app.models.recommendation import RebookingRecommendation


def build_notification_message(
    passenger: Passenger,
    original_flight: Flight,
    recommended_flight: Optional[AlternativeFlight],
    priority: str,
    status: str,
    reason: str
) -> str:
    """
    Generate a deterministic plain-text notification message.
    
    This is a pure function that generates a readable message from recommendation data.
    It does not make database calls or external service calls.
    
    Args:
        passenger: Passenger ORM object
        original_flight: Original flight ORM object
        recommended_flight: Alternative flight ORM object (may be None)
        priority: Priority level string
        status: Recommendation status string
        reason: Reason for the recommendation
        
    Returns:
        Plain-text notification message
    """
    message = f"Rebooking Update\n\n"
    message += f"Passenger: {passenger.name}\n"
    message += f"Original Flight: {original_flight.flight_number}\n"
    
    if recommended_flight:
        message += f"Recommended Flight: {recommended_flight.flight_number}\n"
    else:
        message += f"Recommended Flight: None\n"
    
    message += f"Priority: {priority}\n"
    message += f"Status: {status}\n\n"
    message += f"Reason: {reason}"
    
    return message


async def create_notification(
    passenger_id: UUID,
    recommendation_id: Optional[UUID],
    message: str,
    db: AsyncSession,
    language: str = "English"
) -> Notification:
    """
    Create a new notification.
    
    Args:
        passenger_id: UUID of the passenger
        recommendation_id: UUID of the related recommendation (optional)
        message: Notification message body
        language: Language of the notification (default: English)
        db: Async database session
        
    Returns:
        Created Notification ORM object
    """
    notification = Notification(
        passenger_id=passenger_id,
        recommendation_id=recommendation_id,
        language=language,
        message=message,
        status=NotificationStatus.DRAFT,
        created_at=datetime.now(timezone.utc),
    )
    
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    
    return notification


async def get_notification(
    notification_id: UUID,
    db: AsyncSession
) -> Optional[Notification]:
    """
    Retrieve a notification by ID.
    
    Args:
        notification_id: UUID of the notification
        db: Async database session
        
    Returns:
        Notification ORM object or None if not found
    """
    stmt = select(Notification).where(Notification.notification_id == notification_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_notification_message(
    notification_id: UUID,
    new_message: str,
    db: AsyncSession
) -> Notification:
    """
    Update a notification's message.
    
    Args:
        notification_id: UUID of the notification
        new_message: New message body
        db: Async database session
        
    Returns:
        Updated Notification ORM object
        
    Raises:
        ValueError: If notification not found
    """
    notification = await get_notification(notification_id, db)
    
    if not notification:
        raise ValueError(f"Notification with ID {notification_id} not found")
    
    notification.message = new_message
    
    await db.commit()
    await db.refresh(notification)
    
    return notification


async def send_notification(
    notification_id: UUID,
    db: AsyncSession
) -> Notification:
    """
    Simulate sending a notification.
    
    This is a simulated send - no external service is called.
    It only updates the status to SENT and sets sent_at timestamp.
    
    Args:
        notification_id: UUID of the notification
        db: Async database session
        
    Returns:
        Updated Notification ORM object
        
    Raises:
        ValueError: If notification not found
    """
    notification = await get_notification(notification_id, db)
    
    if not notification:
        raise ValueError(f"Notification with ID {notification_id} not found")
    
    notification.status = NotificationStatus.SENT
    notification.sent_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(notification)
    
    return notification