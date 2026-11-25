from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class OrderItemResponse(BaseModel):
    """Order line item response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    product_id: int
    variant_id: int
    product_title: str
    sku: str
    size: str
    color: str
    unit_price: Decimal
    quantity: int
    line_total: Decimal
    created_at: datetime
