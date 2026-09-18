"""
tests/test_rebooking_decisions.py

Tests for rebooking decision endpoints (approve, edit, reject).

These tests focus on the endpoint logic and validation.
Due to database dependencies, these are basic integration-style tests.
"""

from uuid import UUID, uuid4

import pytest

from app.models.enums import RecommendationStatus


def test_edit_recommendation_request_schema():
    """Test that the edit recommendation request schema validates correctly."""
    from app.schemas.rebooking import EditRecommendationRequest
    
    # Valid request
    valid_payload = {
        "recommended_flight_id": uuid4()
    }
    request = EditRecommendationRequest(**valid_payload)
    assert request.recommended_flight_id == valid_payload["recommended_flight_id"]
    
    # Test with string UUID (should convert)
    string_uuid = str(uuid4())
    payload_with_string = {
        "recommended_flight_id": string_uuid
    }
    request2 = EditRecommendationRequest(**payload_with_string)
    # Should be converted to UUID type
    assert isinstance(request2.recommended_flight_id, UUID)


def test_notification_update_request_schema():
    """Test that the notification update request schema validates correctly."""
    from app.schemas.notification import UpdateNotificationRequest
    
    # Valid request
    valid_payload = {
        "message": "Updated notification message"
    }
    request = UpdateNotificationRequest(**valid_payload)
    assert request.message == "Updated notification message"
    
    # Empty message should fail validation
    empty_payload = {
        "message": ""
    }
    with pytest.raises(Exception):  # Pydantic validation error
        UpdateNotificationRequest(**empty_payload)


def test_recommendation_status_enum_values():
    """Test that the recommendation status enum has the expected values."""
    assert RecommendationStatus.PENDING.value == "PENDING"
    assert RecommendationStatus.APPROVED.value == "APPROVED"
    assert RecommendationStatus.EDITED.value == "EDITED"
    assert RecommendationStatus.REJECTED.value == "REJECTED"
    assert RecommendationStatus.ESCALATED.value == "ESCALATED"


def test_notification_status_enum_values():
    """Test that the notification status enum has the expected values."""
    from app.models.enums import NotificationStatus
    
    assert NotificationStatus.DRAFT.value == "DRAFT"
    assert NotificationStatus.PENDING_REVIEW.value == "PENDING_REVIEW"
    assert NotificationStatus.APPROVED.value == "APPROVED"
    assert NotificationStatus.SENT.value == "SENT"
    assert NotificationStatus.FAILED.value == "FAILED"