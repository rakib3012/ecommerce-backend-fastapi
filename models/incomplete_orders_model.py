from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.users_model import User


class IncompleteOrderStatus(str, Enum):
    """Lifecycle states for abandoned checkout / incomplete order records."""

    ABANDONED = "ABANDONED"
    RECOVERED = "RECOVERED"
    EXPIRED = "EXPIRED"


class IncompleteOrder(Base):
    """Abandoned checkout capture record with single-use 7-day recovery token."""

    __tablename__ = "incomplete_orders"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    customer_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    cart_snapshot: Mapped[list[dict[str, Any]] | dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
    )
    shipping_address_snapshot: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    recovery_token: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        index=True,
        nullable=False,
    )
    recovery_token_expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    recovered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    recovered_order_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("orders.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[IncompleteOrderStatus] = mapped_column(
        SAEnum(IncompleteOrderStatus, name="incomplete_order_status"),
        nullable=False,
        default=IncompleteOrderStatus.ABANDONED,
        server_default=IncompleteOrderStatus.ABANDONED.value,
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
    user: Mapped["User | None"] = relationship(back_populates="incomplete_orders")
