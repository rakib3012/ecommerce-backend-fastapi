from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from models.users_model import UserRole


class UserBase(BaseModel):
    """Shared user fields."""

    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    mobile: str = Field(min_length=1, max_length=20)


class UserCreate(UserBase):
    """Schema for creating a new user account."""

    password: str = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    """Schema for self-service user profile updates."""

    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    mobile: str | None = Field(default=None, min_length=1, max_length=20)


class UserAdminUpdate(UserUpdate):
    """Schema for admin-only user updates."""

    role: UserRole | None = None
    is_active: bool | None = None
    is_verified: bool | None = None


class UserResponse(UserBase):
    """Public/authenticated user response schema (excludes secrets/hashes)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class UserLogin(BaseModel):
    """Schema for email/password login."""

    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    """JWT token pair and authenticated user payload."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
