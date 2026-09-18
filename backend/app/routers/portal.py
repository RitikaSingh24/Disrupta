"""
backend/app/routers/portal.py

Passenger Portal Router.

Endpoints:
  - GET /portal/{token}: Get passenger portal context
  - POST /portal/{token}/requirement: Update passenger requirement

Rules:
  - No JWT authentication required (public portal)
  - Secured by single-use access tokens
  - Uses existing service layer
  - Returns Pydantic response schemas
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.portal import (
    PortalContextResponse,
    PortalRequirementRequest,
    PortalRequirementUpdateResponse,
)
from app.services.portal_service import (
    get_portal_context,
    update_passenger_requirement,
)

router = APIRouter(prefix="/portal", tags=["Portal"])


@router.get(
    "/{token}",
    response_model=PortalContextResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Portal Context",
    description="Retrieve passenger portal context using a valid access token.",
)
async def get_portal(
    token: str,
    db: AsyncSession = Depends(get_db),
) -> PortalContextResponse:
    """
    Get passenger portal context using a valid access token.
    
    No JWT authentication required.
    Returns 404 if token is invalid, expired, or already used.
    """
    context = await get_portal_context(token, db)
    
    if not context:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid, expired, or already-used access token"
        )
    
    return PortalContextResponse(**context)


@router.post(
    "/{token}/requirement",
    response_model=PortalRequirementUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Passenger Requirement",
    description="Update passenger special requirement and re-trigger rebooking analysis.",
)
async def update_requirement(
    token: str,
    payload: PortalRequirementRequest,
    db: AsyncSession = Depends(get_db),
) -> PortalRequirementUpdateResponse:
    """
    Update passenger special requirement and re-trigger rebooking analysis.
    
    No JWT authentication required.
    Returns 404 if token is invalid, expired, or already used.
    Marks token as used after successful update.
    """
    result = await update_passenger_requirement(
        token,
        payload.requirement_type,
        payload.details,
        db
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid, expired, or already-used access token"
        )
    
    return PortalRequirementUpdateResponse(**result)