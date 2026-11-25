from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from models.incomplete_orders_model import IncompleteOrderStatus


class IncompleteOrderCapture(BaseModel):
    """Debounced abandoned checkout capture payload (upserts by session_id)."""

    session_id: str = Field(min_length=1, max_length=120)
    customer_name: str | None = Field(default=None, max_length=150)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=20)
    cart_snapshot: list[dict[str, Any]] | dict[str, Any]
    shipping_address_snapshot: dict[str, Any] | None = None


class IncompleteOrderResponse(BaseModel):
    """Incomplete order response schema (omits raw recovery_token)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: str
    user_id: int | None
    customer_name: str | None
    email: str | None
    phone: str | None
    cart_snapshot: list[dict[str, Any]] | dict[str, Any]
    shipping_address_snapshot: dict[str, Any] | None
    recovery_token_expires_at: datetime
    recovered_at: datetime | None
    recovered_order_id: int | None
    status: IncompleteOrderStatus
    created_at: datetime
    updated_at: datetime
