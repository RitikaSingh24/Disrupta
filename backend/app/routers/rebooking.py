"""
backend/app/routers/rebooking.py

Rebooking Router.

Endpoints:
  - GET /api/v1/rebooking/flight/{flight_id}: Get recommendations for a specific flight
  - POST /api/v1/rebooking/analyze: Analyze affected passengers and generate rebooking recommendations
  - POST /api/v1/rebooking/{recommendation_id}/approve: Approve a rebooking recommendation
  - POST /api/v1/rebooking/{recommendation_id}/edit: Edit a rebooking recommendation
  - POST /api/v1/rebooking/{recommendation_id}/reject: Reject a rebooking recommendation

Rules:
  - Requires JWT authentication via get_current_user
  - Uses existing RebookingRecommendation model
  - Uses existing async database session
  - Returns Pydantic response schemas
  - Handles 404 for nonexistent flights/recommendations
  - Calls rebooking_service for orchestration
"""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import case, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user
from app.db.session import get_db
from app.models.alternative_flight import AlternativeFlight
from app.models.enums import PriorityLevel, RecommendationStatus
from app.models.flight import Flight
from app.models.passenger import Passenger
from app.models.recommendation import RebookingRecommendation
from app.models.user import User
from app.schemas.rebooking import AnalyzeRequest, AnalyzeResponse, EditRecommendationRequest, RecommendationResponse
from app.services.booking_service import get_booking, update_rebooking
from app.services.flight_service import get_affected_passengers
from app.services.rebooking_service import analyze_passenger

router = APIRouter(prefix="/rebooking", tags=["Rebooking"])


@router.get(
    "/flight/{flight_id}",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Recommendations for Flight",
    description="Get existing rebooking recommendations for a specific flight.",
)
async def get_flight_recommendations(
    flight_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AnalyzeResponse:
    """
    Get existing rebooking recommendations for a specific flight.
    
    Requires JWT authentication.
    Returns 404 if flight does not exist.
    """
    # Validate flight exists
    flight_stmt = select(Flight).where(Flight.flight_id == flight_id)
    flight_result = await db.execute(flight_stmt)
    flight = flight_result.scalar_one_or_none()
    
    if not flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flight with ID {flight_id} not found"
        )
    
    # Priority sort order: HIGH=0, MEDIUM=1, NORMAL=2, REVIEW_REQUIRED=3
    priority_order = case(
        (RebookingRecommendation.priority == PriorityLevel.HIGH, 0),
        (RebookingRecommendation.priority == PriorityLevel.MEDIUM, 1),
        (RebookingRecommendation.priority == PriorityLevel.NORMAL, 2),
        (RebookingRecommendation.priority == PriorityLevel.REVIEW_REQUIRED, 3),
        else_=4,
    )

    # Get existing recommendations for this flight with passenger and flight details
    rec_stmt = (
        select(RebookingRecommendation, Passenger, AlternativeFlight)
        .join(Passenger, RebookingRecommendation.passenger_id == Passenger.passenger_id)
        .outerjoin(AlternativeFlight, RebookingRecommendation.recommended_flight_id == AlternativeFlight.alternative_flight_id)
        .where(RebookingRecommendation.original_flight_id == flight_id)
        .order_by(priority_order)
    )
    rec_result = await db.execute(rec_stmt)
    recommendations = rec_result.all()
    
    recommendation_responses = []
    for rec, passenger, alt_flight in recommendations:
        rec_dict = {
            "recommendation_id": rec.recommendation_id,
            "passenger_id": rec.passenger_id,
            "passenger_name": passenger.name,
            "booking_id": rec.booking_id,
            "original_flight_id": rec.original_flight_id,
            "recommended_flight_id": rec.recommended_flight_id,
            "recommended_flight_number": alt_flight.flight_number if alt_flight else None,
            "priority": rec.priority,
            "reason": rec.reason,
            "status": rec.status,
            "version": rec.version,
            "created_at": rec.created_at,
            "updated_at": rec.updated_at,
        }
        recommendation_responses.append(RecommendationResponse(**rec_dict))
    
    return AnalyzeResponse(
        flight_id=flight_id,
        recommendations=recommendation_responses,
        count=len(recommendation_responses)
    )


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Flight for Rebooking",
    description="Analyze all passengers affected by a cancelled flight and generate rebooking recommendations.",
)
async def analyze_flight(
    payload: AnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AnalyzeResponse:
    """
    Analyze a cancelled flight and generate rebooking recommendations for all affected passengers.
    
    Requires JWT authentication.
    Returns 404 if flight does not exist.
    """
    # Validate flight exists
    flight_stmt = select(Flight).where(Flight.flight_id == payload.flight_id)
    flight_result = await db.execute(flight_stmt)
    flight = flight_result.scalar_one_or_none()
    
    if not flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flight with ID {payload.flight_id} not found"
        )
    
    # Get affected passengers using existing service
    try:
        affected_passengers = await get_affected_passengers(payload.flight_id, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    # Analyze each affected passenger
    recommendations = []
    
    for passenger_data in affected_passengers:
        passenger_id = UUID(passenger_data["passenger_id"])
        
        try:
            recommendation = await analyze_passenger(passenger_id, payload.flight_id, db)
            # Fetch passenger name for the response
            passenger_stmt = select(Passenger).where(Passenger.passenger_id == passenger_id)
            passenger_result = await db.execute(passenger_stmt)
            passenger = passenger_result.scalar_one_or_none()
            
            # Fetch recommended flight details
            alt_flight = None
            if recommendation.recommended_flight_id:
                alt_stmt = select(AlternativeFlight).where(AlternativeFlight.alternative_flight_id == recommendation.recommended_flight_id)
                alt_result = await db.execute(alt_stmt)
                alt_flight = alt_result.scalar_one_or_none()
            
            # Create response with passenger name and flight number
            rec_dict = {
                "recommendation_id": recommendation.recommendation_id,
                "passenger_id": recommendation.passenger_id,
                "passenger_name": passenger.name if passenger else None,
                "booking_id": recommendation.booking_id,
                "original_flight_id": recommendation.original_flight_id,
                "recommended_flight_id": recommendation.recommended_flight_id,
                "recommended_flight_number": alt_flight.flight_number if alt_flight else None,
                "priority": recommendation.priority,
                "reason": recommendation.reason,
                "status": recommendation.status,
                "version": recommendation.version,
                "created_at": recommendation.created_at,
                "updated_at": recommendation.updated_at,
            }
            recommendations.append(RecommendationResponse(**rec_dict))
        except ValueError as e:
            # Skip if booking not found or other data issue
            continue
    
    return AnalyzeResponse(
        flight_id=payload.flight_id,
        recommendations=recommendations,
        count=len(recommendations)
    )


@router.post(
    "/{recommendation_id}/approve",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Approve Rebooking Recommendation",
    description="Approve a rebooking recommendation and update the booking's rebooked flight.",
)
async def approve_recommendation(
    recommendation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RecommendationResponse:
    """
    Approve a rebooking recommendation.
    
    This updates both the recommendation status to APPROVED and the booking's rebooked_flight_id.
    Requires JWT authentication.
    Returns 404 if recommendation not found.
    Returns 400 if recommendation has no recommended flight.
    """
    # Fetch recommendation
    rec_stmt = select(RebookingRecommendation).where(RebookingRecommendation.recommendation_id == recommendation_id)
    rec_result = await db.execute(rec_stmt)
    recommendation = rec_result.scalar_one_or_none()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation with ID {recommendation_id} not found"
        )
    
    # Check that recommended flight exists
    if not recommendation.recommended_flight_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot approve recommendation with no recommended flight"
        )
    
    # Update booking using service function
    booking = await update_rebooking(recommendation.booking_id, recommendation.recommended_flight_id, db)
    
    # Update recommendation status
    recommendation.status = RecommendationStatus.APPROVED
    recommendation.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(recommendation)
    
    return RecommendationResponse.model_validate(recommendation)


@router.post(
    "/{recommendation_id}/edit",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Edit Rebooking Recommendation",
    description="Edit a rebooking recommendation by changing the recommended flight.",
)
async def edit_recommendation(
    recommendation_id: UUID,
    payload: EditRecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RecommendationResponse:
    """
    Edit a rebooking recommendation by changing the recommended flight.
    
    This does NOT update the booking's rebooked_flight_id.
    The booking is only updated when the recommendation is approved.
    Requires JWT authentication.
    Returns 404 if recommendation not found.
    Returns 404 if the new recommended flight does not exist.
    """
    # Fetch recommendation
    rec_stmt = select(RebookingRecommendation).where(RebookingRecommendation.recommendation_id == recommendation_id)
    rec_result = await db.execute(rec_stmt)
    recommendation = rec_result.scalar_one_or_none()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation with ID {recommendation_id} not found"
        )
    
    # Validate the new recommended flight exists
    alt_flight_stmt = select(AlternativeFlight).where(AlternativeFlight.alternative_flight_id == payload.recommended_flight_id)
    alt_flight_result = await db.execute(alt_flight_stmt)
    alt_flight = alt_flight_result.scalar_one_or_none()
    
    if not alt_flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alternative flight with ID {payload.recommended_flight_id} not found"
        )
    
    # Update recommendation
    recommendation.recommended_flight_id = payload.recommended_flight_id
    recommendation.status = RecommendationStatus.EDITED
    recommendation.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(recommendation)
    
    return RecommendationResponse.model_validate(recommendation)


@router.post(
    "/{recommendation_id}/reject",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Reject Rebooking Recommendation",
    description="Reject a rebooking recommendation.",
)
async def reject_recommendation(
    recommendation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RecommendationResponse:
    """
    Reject a rebooking recommendation.
    
    This does NOT update the booking's rebooked_flight_id.
    Requires JWT authentication.
    Returns 404 if recommendation not found.
    """
    # Fetch recommendation
    rec_stmt = select(RebookingRecommendation).where(RebookingRecommendation.recommendation_id == recommendation_id)
    rec_result = await db.execute(rec_stmt)
    recommendation = rec_result.scalar_one_or_none()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation with ID {recommendation_id} not found"
        )
    
    # Update recommendation status
    recommendation.status = RecommendationStatus.REJECTED
    recommendation.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(recommendation)
    
    return RecommendationResponse.model_validate(recommendation)