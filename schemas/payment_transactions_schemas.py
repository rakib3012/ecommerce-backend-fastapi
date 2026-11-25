from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from models.payment_transactions_model import PaymentTransactionStatus


class PaymentInitiationRequest(BaseModel):
    """Request to initiate a payment transaction for an order."""

    order_id: int = Field(gt=0)


class PaymentTransactionResponse(BaseModel):
    """Payment transaction response schema (omits raw gateway secrets/payloads)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    tran_id: str
    val_id: str | None
    provider: str
    amount: Decimal
    currency: str
    status: PaymentTransactionStatus
    verified_at: datetime | None
    created_at: datetime
    updated_at: datetime
