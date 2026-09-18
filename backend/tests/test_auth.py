"""
backend/tests/test_auth.py

Comprehensive Unit & Integration Test Suite for Authentication and Security Foundation.

Tests:
  - Password hashing and verification.
  - JWT token creation, decoding, and expiration validation.
  - POST /auth/login route (success, invalid password, nonexistent user).
  - get_current_user dependency.
  - require_role authorization dependency.
"""

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock
import uuid

import pytest
from fastapi import HTTPException, status
from httpx import ASGITransport, AsyncClient

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.deps import get_current_user, require_role
from app.main import app
from app.models.enums import UserRole
from app.models.user import User


# ── 1. Security Utilities Unit Tests ───────────────────────────────────────
class TestSecurityUtilities:
    def test_hash_and_verify_password(self):
        plain = "MySecretPass123!"
        hashed = hash_password(plain)

        assert hashed != plain
        assert verify_password(plain, hashed) is True
        assert verify_password("WrongPass", hashed) is False

    def test_create_and_decode_access_token(self):
        subject = str(uuid.uuid4())
        token = create_access_token(data={"sub": subject})

        decoded = decode_access_token(token)
        assert decoded.get("sub") == subject
        assert "exp" in decoded

    def test_decode_invalid_token(self):
        with pytest.raises(ValueError, match="Invalid or expired token"):
            decode_access_token("invalid.jwt.token.string")

    def test_decode_expired_token(self):
        subject = str(uuid.uuid4())
        token = create_access_token(
            data={"sub": subject},
            expires_delta=timedelta(seconds=-10),  # expired 10 seconds ago
        )

        with pytest.raises(ValueError, match="Invalid or expired token"):
            decode_access_token(token)


# ── 2. Login API Integration Tests ──────────────────────────────────────────
@pytest.mark.asyncio
class TestLoginEndpoint:
    async def test_login_success(self):
        # Create mock user
        user_id = uuid.uuid4()
        user = User(
            user_id=user_id,
            name="Alice Agent",
            email="alice@airline.com",
            password_hash=hash_password("SuperPassword123!"),
            role=UserRole.OPERATIONS_AGENT,
        )

        # Mock DB session
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = user
        mock_session.execute.return_value = mock_result

        async def override_db():
            yield mock_session

        app.dependency_overrides[get_db] = override_db
        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/auth/login",
                    json={
                        "email": "alice@airline.com",
                        "password": "SuperPassword123!",
                    },
                )

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"

            # Verify token contents
            payload = decode_access_token(data["access_token"])
            assert payload["sub"] == str(user_id)
        finally:
            app.dependency_overrides.clear()

    async def test_login_invalid_password(self):
        user = User(
            user_id=uuid.uuid4(),
            name="Alice Agent",
            email="alice@airline.com",
            password_hash=hash_password("SuperPassword123!"),
            role=UserRole.OPERATIONS_AGENT,
        )

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = user
        mock_session.execute.return_value = mock_result

        async def override_db():
            yield mock_session

        app.dependency_overrides[get_db] = override_db
        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/auth/login",
                    json={
                        "email": "alice@airline.com",
                        "password": "WrongPassword",
                    },
                )

            assert response.status_code == 401
            assert response.json()["detail"] == "Invalid email or password"
        finally:
            app.dependency_overrides.clear()

    async def test_login_nonexistent_email(self):
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        async def override_db():
            yield mock_session

        app.dependency_overrides[get_db] = override_db
        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/auth/login",
                    json={
                        "email": "nonexistent@airline.com",
                        "password": "SuperPassword123!",
                    },
                )

            assert response.status_code == 401
            assert response.json()["detail"] == "Invalid email or password"
        finally:
            app.dependency_overrides.clear()

    async def test_login_invalid_payload(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/auth/login",
                json={
                    "email": "not-an-email",
                },
            )

        assert response.status_code == 422


# ── 3. Authentication & Role Dependencies Unit Tests ───────────────────────
@pytest.mark.asyncio
class TestAuthDependencies:
    async def test_get_current_user_valid_token(self):
        user_id = uuid.uuid4()
        user = User(
            user_id=user_id,
            name="Alice Agent",
            email="alice@airline.com",
            password_hash="hash",
            role=UserRole.OPERATIONS_AGENT,
        )
        token = create_access_token(data={"sub": str(user_id)})

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = user
        mock_session.execute.return_value = mock_result

        current_user = await get_current_user(token=token, db=mock_session)
        assert current_user.user_id == user_id
        assert current_user.email == "alice@airline.com"

    async def test_get_current_user_invalid_token(self):
        mock_session = AsyncMock()
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token="invalid.token", db=mock_session)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_current_user_missing_token(self):
        mock_session = AsyncMock()
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=None, db=mock_session)
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_require_role_permitted(self):
        user = User(
            user_id=uuid.uuid4(),
            name="Alice Agent",
            email="alice@airline.com",
            password_hash="hash",
            role=UserRole.OPERATIONS_AGENT,
        )
        role_checker = require_role(UserRole.OPERATIONS_AGENT, UserRole.ADMIN)
        result_user = await role_checker(current_user=user)
        assert result_user.user_id == user.user_id

    async def test_require_role_forbidden(self):
        user = User(
            user_id=uuid.uuid4(),
            name="Alice Agent",
            email="alice@airline.com",
            password_hash="hash",
            role=UserRole.OPERATIONS_AGENT,
        )
        role_checker = require_role(UserRole.ADMIN)
        with pytest.raises(HTTPException) as exc_info:
            await role_checker(current_user=user)
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc_info.value.detail == "Insufficient privileges"
