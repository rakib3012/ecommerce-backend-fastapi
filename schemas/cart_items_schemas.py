from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CartItemBase(BaseModel):
    """Shared cart item fields."""

    variant_id: int = Field(gt=0)
    quantity: int = Field(default=1, ge=1)


class CartItemCreate(CartItemBase):
    """Schema for adding an item to the cart."""


class CartItemUpdate(BaseModel):
    """Schema for updating cart item quantity."""

    quantity: int = Field(ge=1)


class CartItemResponse(CartItemBase):
    """Cart item response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    cart_id: int
    created_at: datetime
    updated_at: datetime
