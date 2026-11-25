from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AddressBase(BaseModel):
    """Shared address fields."""

    label: str | None = Field(default=None, max_length=50)
    recipient_name: str = Field(min_length=1, max_length=150)
    phone: str = Field(min_length=1, max_length=20)
    street_address: str = Field(min_length=1, max_length=255)
    area: str | None = Field(default=None, max_length=100)
    city: str = Field(min_length=1, max_length=100)
    district: str = Field(min_length=1, max_length=100)
    postal_code: str | None = Field(default=None, max_length=20)
    country: str = Field(default="Bangladesh", min_length=1, max_length=100)
    is_default: bool = False


class AddressCreate(AddressBase):
    """Schema for creating a user address (user_id is derived from auth)."""


class AddressUpdate(BaseModel):
    """Schema for partial updates to an existing user address."""

    label: str | None = Field(default=None, max_length=50)
    recipient_name: str | None = Field(default=None, min_length=1, max_length=150)
    phone: str | None = Field(default=None, min_length=1, max_length=20)
    street_address: str | None = Field(default=None, min_length=1, max_length=255)
    area: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, min_length=1, max_length=100)
    district: str | None = Field(default=None, min_length=1, max_length=100)
    postal_code: str | None = Field(default=None, max_length=20)
    country: str | None = Field(default=None, min_length=1, max_length=100)
    is_default: bool | None = None


class AddressResponse(AddressBase):
    """Address response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
