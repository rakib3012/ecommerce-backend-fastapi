from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductVariantBase(BaseModel):
    """Shared SKU variant fields."""

    product_id: int = Field(gt=0)
    sku: str = Field(min_length=1, max_length=80)
    size: str = Field(min_length=1, max_length=40)
    color: str = Field(min_length=1, max_length=60)
    color_hex: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    price_override: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    stock: int = Field(default=0, ge=0)
    is_active: bool = True


class ProductVariantCreate(ProductVariantBase):
    """Schema for creating a product variant."""


class ProductVariantUpdate(BaseModel):
    """Schema for partial updates to a product variant."""

    sku: str | None = Field(default=None, min_length=1, max_length=80)
    size: str | None = Field(default=None, min_length=1, max_length=40)
    color: str | None = Field(default=None, min_length=1, max_length=60)
    color_hex: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    price_override: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    stock: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class ProductVariantResponse(ProductVariantBase):
    """Product variant response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
