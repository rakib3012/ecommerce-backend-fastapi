from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CartItemSummary(BaseModel):
    """Embedded cart item summary inside CartResponse."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    variant_id: int
    quantity: int
    created_at: datetime
    updated_at: datetime


class CartResponse(BaseModel):
    """Shopping cart response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None
    session_id: str | None
    items: list[CartItemSummary] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
