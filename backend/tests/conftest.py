"""
tests/conftest.py

Shared pytest fixtures for test configuration.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.db.session import AsyncSessionLocal
from app.main import app
from app.models.user import User


@pytest.fixture
async def db():
    """Provide a database session for tests."""
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def auth_token(db: AsyncSession):
    """Get auth token for existing seeded user (agent@airline.com)."""
    # Use existing seeded user instead of creating new one
    stmt = select(User).where(User.email == "agent@airline.com")
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        pytest.skip("Seeded user agent@airline.com not found")
    
    # Generate token
    token = create_access_token(data={"sub": str(user.user_id)})
    return token


@pytest.fixture
def async_client():
    """Provide an async HTTP client for testing."""
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")