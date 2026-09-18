"""
backend/app/core/security.py

Security & Cryptographic Utilities.

Responsibilities:
  - Hash passwords using bcrypt.
  - Verify plain passwords against bcrypt hashes.
  - Create signed JWT access tokens containing user subject ('sub') and expiration.
  - Decode and verify JWT tokens.

Rules:
  - Reads configuration (JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES) from app.core.config.
  - Does NOT handle database logic or routes.
  - Does NOT store plaintext passwords.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# ── Password context ────────────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Generate a signed JWT access token.

    :param data: Claims to encode (e.g. {"sub": str(user_id)}).
    :param expires_delta: Optional expiration override. Defaults to JWT_EXPIRE_MINUTES.
    :return: Encoded JWT string.
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": now})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and verify a JWT access token.

    :param token: The JWT token string.
    :return: Decoded claims dictionary.
    :raises ValueError: If token signature is invalid, expired, or malformed.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError as exc:
        raise ValueError(f"Invalid or expired token: {str(exc)}") from exc
