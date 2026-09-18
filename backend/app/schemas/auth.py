"""
backend/app/schemas/auth.py

Pydantic v2 schemas for authentication requests and responses.

Rules:
  - Only contains schemas required for login.
  - No database models or logic.
"""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    """Payload for POST /auth/login."""

    email: EmailStr = Field(..., description="User's registered email address")
    password: str = Field(..., min_length=1, description="Plaintext password")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "agent@airline.com",
                "password": "SecretPassword123!",
            }
        }
    )


class TokenResponse(BaseModel):
    """Response returned upon successful login."""

    access_token: str = Field(..., description="JWT bearer token")
    token_type: str = Field(default="bearer", description="Token type")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
            }
        }
    )
