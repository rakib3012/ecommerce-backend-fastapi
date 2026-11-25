from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from models.orders_model import (
    DeliveryZone,
    OrderStatus,
    PaymentMethod,
    PaymentStatus,
)
from schemas.order_items_schemas import OrderItemResponse


class OrderCheckoutItemInput(BaseModel):
    """Variant and quantity requested at checkout."""

    variant_id: int = Field(gt=0)
    quantity: int = Field(ge=1)


class OrderCreate(BaseModel):
    """Server-authoritative checkout request (no client-supplied totals/statuses)."""

    address_id: int | None = Field(default=None, gt=0)
    shipping_address_snapshot: dict[str, Any] | None = None
    delivery_zone: DeliveryZone
    payment_method: PaymentMethod
    coupon_code: str | None = Field(default=None, max_length=60)
    items: list[OrderCheckoutItemInput] | None = None
    notes: str | None = Field(default=None, max_length=1000)


class OrderStatusUpdate(BaseModel):
    """Admin-only order status update schema."""

    status: OrderStatus


class OrderResponse(BaseModel):
    """Order response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    user_id: int | None
    shipping_address_snapshot: dict[str, Any]
    delivery_zone: DeliveryZone
    coupon_code: str | None
    subtotal: Decimal
    discount_amount: Decimal
    delivery_fee: Decimal
    total_amount: Decimal
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    status: OrderStatus
    notes: str | None
    items: list[OrderItemResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
