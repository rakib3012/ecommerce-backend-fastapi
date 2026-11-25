from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductAttributeBase(BaseModel):
    """Shared product attribute fields."""

    product_id: int = Field(gt=0)
    attribute_name: str = Field(min_length=1, max_length=100)
    attribute_value: str = Field(min_length=1, max_length=255)
    display_order: int = Field(default=0, ge=0)


class ProductAttributeCreate(ProductAttributeBase):
    """Schema for creating a product attribute."""


class ProductAttributeUpdate(BaseModel):
    """Schema for partial updates to a product attribute."""

    attribute_name: str | None = Field(default=None, min_length=1, max_length=100)
    attribute_value: str | None = Field(default=None, min_length=1, max_length=255)
    display_order: int | None = Field(default=None, ge=0)


class ProductAttributeResponse(ProductAttributeBase):
    """Product attribute response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
