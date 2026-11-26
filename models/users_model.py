from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.addresses_model import Address
    from models.carts_model import Cart
    from models.incomplete_orders_model import IncompleteOrder
    from models.orders_model import Order
    from models.wishlists_model import Wishlist


class UserRole(str, Enum):
    """Allowed user roles."""

    CUSTOMER = "CUSTOMER"
    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"
    


class User(Base):
    """Persisted user account for customers and admins."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    mobile: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role"),
        nullable=False,
        default=UserRole.CUSTOMER,
        server_default=UserRole.CUSTOMER.value,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    otp_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    otp_expires_at: Mapped[datetime | None] = mapped_column(
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

    # --- Relationships ---
    # 1. One-to-Many: Ekjon user-er ekadhik address thakte pare (user delete hole address-o delete hoye jabe)
    addresses: Mapped[list["Address"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # 2. One-to-One: Ekjon user-er sudhu ekta active cart thakbe (tai uselist=False dewa hoyeche)
    cart: Mapped["Cart | None"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # 3. One-to-Many: User-er wishlist-e rakha product gulo
    wishlists: Mapped[list["Wishlist"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # 4. One-to-Many: User-er sob order history (user delete holeo order record rakha valo, tai delete-orphan dewa hoyni)
    orders: Mapped[list["Order"]] = relationship(
        back_populates="user",
    )

    # 5. One-to-Many: User jodi checkout complete na kore drop kore, tar abandoned checkout list
    incomplete_orders: Mapped[list["IncompleteOrder"]] = relationship(
        back_populates="user",
    )