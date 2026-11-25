from datetime import datetime, timedelta, timezone
from typing import Any, Literal
import uuid

import bcrypt
import jwt

from core import config

ACCESS_TOKEN_EXPIRE_MINUTES: int = getattr(config, "ACCESS_TOKEN_EXPIRE_MINUTES", 15)
REFRESH_TOKEN_EXPIRE_DAYS: int = getattr(config, "REFRESH_TOKEN_EXPIRE_DAYS", 7)

TokenType = Literal["access", "refresh"]


class TokenError(Exception):
    """Raised when a JWT is invalid, expired, or has an unexpected type."""


def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify a plain-text password against a stored bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        password_hash.encode("utf-8"),
    )


def encode_token(
    subject: str | int,
    token_type: TokenType,
    role: str,
    expires_delta: timedelta,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Encode a signed JWT with standard claims (sub, type, role, jti, iat, exp)."""
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "type": token_type,
        "role": role,
        "jti": uuid.uuid4().hex,
        "iat": now,
        "exp": now + expires_delta,
    }
    if extra_claims:
        for key, value in extra_claims.items():
            if key not in {"sub", "type", "role", "jti", "iat", "exp"}:
                payload[key] = value

    return jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM)


def decode_token(
    token: str,
    expected_type: TokenType | None = None,
) -> dict[str, Any]:
    """Decode and validate a JWT, optionally enforcing its token type."""
    try:
        payload = jwt.decode(
            token,
            config.SECRET_KEY,
            algorithms=[config.ALGORITHM],
            options={"require": ["exp", "iat", "sub", "jti", "type"]},
        )
    except jwt.ExpiredSignatureError as exc:
        raise TokenError("Token has expired.") from exc
    except jwt.InvalidTokenError as exc:
        raise TokenError("Invalid authentication token.") from exc

    if expected_type is not None and payload.get("type") != expected_type:
        raise TokenError(f"Invalid token type: expected '{expected_type}'.")

    return payload


def create_access_token(
    subject: str | int,
    role: str,
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Create a short-lived access JWT."""
    delta = expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return encode_token(
        subject=subject,
        token_type="access",
        role=role,
        expires_delta=delta,
        extra_claims=extra_claims,
    )


def create_refresh_token(
    subject: str | int,
    role: str,
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Create a refresh JWT with a unique jti for rotation/blacklisting."""
    delta = expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    return encode_token(
        subject=subject,
        token_type="refresh",
        role=role,
        expires_delta=delta,
        extra_claims=extra_claims,
    )


def create_token_pair(
    subject: str | int,
    role: str,
    extra_claims: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Create both access and refresh tokens for an authenticated user."""
    return {
        "access_token": create_access_token(
            subject=subject,
            role=role,
            extra_claims=extra_claims,
        ),
        "refresh_token": create_refresh_token(
            subject=subject,
            role=role,
            extra_claims=extra_claims,
        ),
        "token_type": "bearer",
    }
