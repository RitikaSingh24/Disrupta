"""
backend/app/routers/dashboard.py

Dashboard Router.

Endpoints:
  - GET /dashboard/overview: Get dashboard overview statistics

Rules:
  - Requires JWT authentication via get_current_user
  - Uses existing async database session
  - Returns Pydantic response schemas
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardOverviewResponse
from app.services.dashboard_service import get_dashboard_overview

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/overview",
    response_model=DashboardOverviewResponse,
    summary="Get Dashboard Overview",
    description="Retrieve overview statistics for the dashboard.",
)
async def get_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DashboardOverviewResponse:
    """
    Get dashboard overview statistics.
    
    Requires JWT authentication.
    """
    overview = await get_dashboard_overview(db)
    return DashboardOverviewResponse(**overview)