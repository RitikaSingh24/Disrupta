"""
tests/test_portal.py

Tests for the passenger portal service and router.

These tests verify that the portal functions exist and have the correct signatures.
They do not require database connection for basic structure verification.
"""

import pytest
from uuid import uuid4

from app.services.portal_service import (
    generate_portal_tokens,
    validate_token,
    get_portal_context,
    update_passenger_requirement,
)
from app.schemas.portal import (
    PortalRequirementRequest,
    PortalContextResponse,
    PortalRequirementUpdateResponse,
)


def test_portal_service_functions_exist():
    """Test that portal service functions are defined and callable."""
    assert callable(generate_portal_tokens)
    assert callable(validate_token)
    assert callable(get_portal_context)
    assert callable(update_passenger_requirement)


def test_portal_schemas_exist():
    """Test that portal schemas are defined."""
    assert PortalRequirementRequest is not None
    assert PortalContextResponse is not None
    assert PortalRequirementUpdateResponse is not None


def test_portal_requirement_request_schema():
    """Test that portal requirement request schema has expected fields."""
    assert hasattr(PortalRequirementRequest, 'model_fields')
    fields = PortalRequirementRequest.model_fields.keys()
    assert 'requirement_type' in fields
    assert 'details' in fields


def test_portal_functions_signature():
    """Test that portal functions have expected signatures."""
    import inspect
    
    # generate_portal_tokens signature
    sig = inspect.signature(generate_portal_tokens)
    params = list(sig.parameters.keys())
    assert 'flight_id' in params
    assert 'passenger_ids' in params
    assert 'db' in params
    
    # validate_token signature
    sig = inspect.signature(validate_token)
    params = list(sig.parameters.keys())
    assert 'token' in params
    assert 'db' in params
    
    # get_portal_context signature
    sig = inspect.signature(get_portal_context)
    params = list(sig.parameters.keys())
    assert 'token' in params
    assert 'db' in params
    
    # update_passenger_requirement signature
    sig = inspect.signature(update_passenger_requirement)
    params = list(sig.parameters.keys())
    assert 'token' in params
    assert 'requirement_type' in params
    assert 'details' in params
    assert 'db' in params


def test_portal_requirement_request_validation():
    """Test that portal requirement request validates correctly."""
    # Valid request
    valid_request = PortalRequirementRequest(
        requirement_type="Medical Assistance",
        details="Wheelchair assistance required"
    )
    assert valid_request.requirement_type == "Medical Assistance"
    assert valid_request.details == "Wheelchair assistance required"
    
    # Missing required field should raise validation error
    with pytest.raises(Exception):
        PortalRequirementRequest(requirement_type="Medical Assistance")  # Missing details