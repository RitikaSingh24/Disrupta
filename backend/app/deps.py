"""
backend/app/deps.py

FastAPI Authentication & Authorization Dependencies.

Dependencies:
  - get_current_user: Validates JWT Bearer token and returns the authenticated User ORM object.
  - require_role: Role-based authorization dependency factory.

Rules:
  - Reuses existing db session dependency (get_db).
  - Reuses existing User model (app.models.user.User) and UserRole enum (app.models.enums.UserRole).
  - Returns HTTP 401 Unauthorized for authentication/token failures.
  - Returns HTTP 403 Forbidden for insufficient role permissions.
"""

import uuid
from typing import Callable, Sequence

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User

# OAuth2 Scheme — points to the login endpoint URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Extract and validate JWT token from Authorization Bearer header,
    query the database for the corresponding user, and return the User model.

    Raises:
        HTTPException 401 if token is missing, invalid, expired, or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    try:
        payload = decode_access_token(token)
        user_id_str: str | None = payload.get("sub")
        if not user_id_str:
            raise credentials_exception
        user_id = uuid.UUID(user_id_str)
    except (ValueError, TypeError):
        raise credentials_exception

    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


def require_role(*allowed_roles: UserRole) -> Callable[..., User]:
    """
    Dependency factory to enforce role-based access control.

    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_role(UserRole.ADMIN))])
        async def admin_route(): ...
    """

    async def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient privileges",
            )
        return current_user

    return role_checker
