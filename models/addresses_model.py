from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

# Circular import avoid korar jonno TYPE_CHECKING use kora hoyeche:
# users_model.py ebong addresses_model.py duitai ek-oporke reference kore.
# Runtime-e TYPE_CHECKING False thake, tai User import hoy na ebong circular import error hoy na;
# kintu IDE/type-checker (mypy/pyright) eta True dhore autocomplete o type check korte pare.
if TYPE_CHECKING:
    from models.users_model import User


class Address(Base):
    """Persisted shipping/billing address belonging to a user."""

    __tablename__ = "addresses"

    # Table-e extra database-level constraint ba index add korar jonno __table_args__ use hoy.
    # Ekhane partial unique index dewa hoyeche jate PostgreSQL level-ei guarantee thake:
    # ekjon user-er ekadhik address thakleo tar moddhe sudhu 1ta address-i is_default=True hote parbe.
    __table_args__ = (
        Index(
            "uq_addresses_user_default",
            "user_id",
            unique=True,
            postgresql_where=text("is_default IS TRUE"),
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    label: Mapped[str | None] = mapped_column(String(50), nullable=True)
    recipient_name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    street_address: Mapped[str] = mapped_column(String(255), nullable=False)
    area: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Bangladesh",
        server_default="Bangladesh",
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
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
    user: Mapped["User"] = relationship(back_populates="addresses")
