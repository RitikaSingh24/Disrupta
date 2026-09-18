"""
backend/app/routers/auth.py

Authentication Router.

Endpoints:
  - POST /auth/login: Authenticates employee credentials and returns a JWT access token.

Rules:
  - Uses existing Users table (app.models.user.User).
  - Uses get_db async session dependency.
  - Returns 401 Unauthorized with generic message on authentication failure.
  - Does NOT reveal whether email exists or password was incorrect.
  - Does NOT create users or implement registration/refresh/logout in this phase.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticate with email and password to receive a JWT access token.",
)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Authenticate an operations agent / supervisor / admin user.

    1. Search for user by email (case-insensitive strip).
    2. Verify password against stored hash.
    3. If invalid, return 401 Unauthorized.
    4. If valid, return JWT bearer token.
    """
    email_clean = payload.email.strip().lower()

    # Query existing users table
    stmt = select(User).where(User.email == email_clean)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    # Generic authentication failure check
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate JWT token with sub=str(user_id)
    access_token = create_access_token(data={"sub": str(user.user_id)})

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )
