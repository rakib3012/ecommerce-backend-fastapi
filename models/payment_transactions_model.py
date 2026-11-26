from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.orders_model import Order


class PaymentTransactionStatus(str, Enum):
    """Allowed payment transaction verification states."""

    INITIATED = "INITIATED"
    VALIDATED = "VALIDATED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class PaymentTransaction(Base):
    """Idempotent payment gateway transaction record (unique tran_id)."""

    __tablename__ = "payment_transactions"
    __table_args__ = (
        CheckConstraint("amount >= 0", name="ck_payment_transactions_amount_non_negative"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tran_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    val_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    provider: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="SSLCOMMERZ",
        server_default="SSLCOMMERZ",
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="BDT",
        server_default="BDT",
    )
    status: Mapped[PaymentTransactionStatus] = mapped_column(
        SAEnum(PaymentTransactionStatus, name="payment_transaction_status"),
        nullable=False,
        default=PaymentTransactionStatus.INITIATED,
        server_default=PaymentTransactionStatus.INITIATED.value,
    )
    raw_payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # relationship
    order: Mapped["Order"] = relationship(back_populates="payment_transactions")
