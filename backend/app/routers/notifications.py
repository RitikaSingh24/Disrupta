"""
backend/app/routers/notifications.py

Notification Router.

Endpoints:
  - POST /api/v1/notifications/{notification_id}/send: Simulate sending a notification
  - PATCH /api/v1/notifications/{notification_id}: Update a notification message

Rules:
  - Requires JWT authentication via get_current_user
  - Uses existing Notification model
  - Uses existing async database session
  - Returns Pydantic response schemas
  - Handles 404 for nonexistent notifications
  - Handles 400/409 for invalid state transitions
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user
from app.db.session import get_db
from app.models.enums import NotificationStatus
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationResponse, UpdateNotificationRequest
from app.services.notification_service import get_notification, send_notification, update_notification_message

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post(
    "/{notification_id}/send",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Send Notification",
    description="Simulate sending a notification by updating its status to SENT.",
)
async def send_notification_endpoint(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NotificationResponse:
    """
    Simulate sending a notification.
    
    This only updates the status to SENT and sets sent_at timestamp.
    No external service is called.
    Requires JWT authentication.
    Returns 404 if notification not found.
    Returns 409 if notification is already sent.
    """
    # Fetch notification
    notification = await get_notification(notification_id, db)
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with ID {notification_id} not found"
        )
    
    # Check if already sent
    if notification.status == NotificationStatus.SENT:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Notification has already been sent"
        )
    
    # Simulate send
    notification = await send_notification(notification_id, db)
    
    return NotificationResponse.model_validate(notification)


@router.patch(
    "/{notification_id}",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Notification",
    description="Update a notification's message.",
)
async def update_notification_endpoint(
    notification_id: UUID,
    payload: UpdateNotificationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NotificationResponse:
    """
    Update a notification's message.
    
    Requires JWT authentication.
    Returns 404 if notification not found.
    Returns 400 if message is empty.
    Returns 409 if notification is already sent.
    """
    # Fetch notification
    notification = await get_notification(notification_id, db)
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with ID {notification_id} not found"
        )
    
    # Check if already sent
    if notification.status == NotificationStatus.SENT:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot edit a notification that has already been sent"
        )
    
    # Update message
    notification = await update_notification_message(notification_id, payload.message, db)
    
    return NotificationResponse.model_validate(notification)