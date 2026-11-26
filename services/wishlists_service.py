from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.products_model import Product
from models.users_model import User
from models.wishlists_model import Wishlist
from schemas.wishlists_schemas import WishlistCreate


class WishlistServiceError(Exception):
    """Domain error raised by wishlist service operations."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


async def list_wishlist_items(
    database_session: AsyncSession,
    current_user: User,
) -> list[Wishlist]:
    """List all wishlist items belonging to the authenticated user."""
    result = await database_session.execute(
        select(Wishlist)
        .where(Wishlist.user_id == current_user.id)
        .order_by(Wishlist.created_at.desc(), Wishlist.id.desc())
    )
    return list(result.scalars().all())


async def add_to_wishlist(
    database_session: AsyncSession,
    payload: WishlistCreate,
    current_user: User,
) -> Wishlist:
    """Add a product to the user's wishlist safely (idempotent on duplicates)."""
    product_result = await database_session.execute(
        select(Product.id).where(
            Product.id == payload.product_id,
            Product.is_active.is_(True),
        )
    )
    if product_result.scalar_one_or_none() is None:
        raise WishlistServiceError(status_code=404, detail="Product not found.")

    existing_result = await database_session.execute(
        select(Wishlist).where(
            Wishlist.user_id == current_user.id,
            Wishlist.product_id == payload.product_id,
        )
    )
    existing_item = existing_result.scalar_one_or_none()
    if existing_item is not None:
        return existing_item

    wishlist_record = Wishlist(
        user_id=current_user.id,
        product_id=payload.product_id,
    )
    database_session.add(wishlist_record)
    try:
        await database_session.commit()
        await database_session.refresh(wishlist_record)
    except IntegrityError:
        await database_session.rollback()
        retry_result = await database_session.execute(
            select(Wishlist).where(
                Wishlist.user_id == current_user.id,
                Wishlist.product_id == payload.product_id,
            )
        )
        existing_after_race = retry_result.scalar_one_or_none()
        if existing_after_race is not None:
            return existing_after_race
        raise

    return wishlist_record


async def remove_from_wishlist(
    database_session: AsyncSession,
    product_id: int,
    current_user: User,
) -> None:
    """Remove a product from the authenticated user's wishlist."""
    result = await database_session.execute(
        select(Wishlist).where(
            Wishlist.user_id == current_user.id,
            Wishlist.product_id == product_id,
        )
    )
    wishlist_record = result.scalar_one_or_none()
    if wishlist_record is None:
        raise WishlistServiceError(status_code=404, detail="Wishlist item not found.")

    await database_session.delete(wishlist_record)
    await database_session.commit()
