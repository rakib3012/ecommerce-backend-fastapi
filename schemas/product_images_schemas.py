from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductImageBase(BaseModel):
    """Shared product image fields."""

    product_id: int = Field(gt=0)
    variant_id: int | None = Field(default=None, gt=0)
    image_url: str = Field(min_length=1, max_length=500)
    alt_text: str | None = Field(default=None, max_length=200)
    display_order: int = Field(default=0, ge=0)
    is_primary: bool = False


class ProductImageCreate(ProductImageBase):
    """Schema for creating a product image."""


class ProductImageUpdate(BaseModel):
    """Schema for partial updates to a product image."""

    variant_id: int | None = Field(default=None, gt=0)
    image_url: str | None = Field(default=None, min_length=1, max_length=500)
    alt_text: str | None = Field(default=None, max_length=200)
    display_order: int | None = Field(default=None, ge=0)
    is_primary: bool | None = None


class ProductImageResponse(ProductImageBase):
    """Product image response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
