from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WishlistCreate(BaseModel):
    """Schema for adding a product to the authenticated user's wishlist."""

    product_id: int = Field(gt=0)


class WishlistResponse(BaseModel):
    """Wishlist item response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    product_id: int
    created_at: datetime
