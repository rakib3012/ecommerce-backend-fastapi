from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.cart_items_model import CartItem
from models.carts_model import Cart
from models.product_variants_model import ProductVariant
from models.users_model import User


class CartServiceError(Exception):
    """Domain error raised by cart service operations."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def resolve_cart_owner(
    current_user: User | None,
    session_id: str | None,
) -> tuple[int | None, str | None]:
    """Resolve authenticated user_id or guest session_id, raising 400 if neither is present."""
    if current_user is not None:
        return current_user.id, None
    cleaned_session_id = session_id.strip() if session_id else ""
    if not cleaned_session_id:
        raise CartServiceError(
            status_code=400,
            detail="Authentication or X-Session-Id header is required.",
        )
    return None, cleaned_session_id


async def _fetch_cart_with_items(
    database_session: AsyncSession,
    user_id: int | None,
    session_id: str | None,
) -> Cart | None:
    statement = select(Cart).options(selectinload(Cart.items))
    if user_id is not None:
        statement = statement.where(Cart.user_id == user_id)
    else:
        statement = statement.where(Cart.session_id == session_id)
    result = await database_session.execute(statement)
    return result.scalar_one_or_none()


async def get_or_create_cart(
    database_session: AsyncSession,
    current_user: User | None,
    session_id: str | None,
) -> Cart:
    """Fetch or create the active cart for an authenticated user or guest session."""
    user_id, resolved_session_id = resolve_cart_owner(current_user, session_id)
    cart_record = await _fetch_cart_with_items(
        database_session,
        user_id=user_id,
        session_id=resolved_session_id,
    )
    if cart_record is not None:
        return cart_record

    cart_record = Cart(
        user_id=user_id,
        session_id=resolved_session_id,
    )
    database_session.add(cart_record)
    try:
        await database_session.commit()
    except IntegrityError:
        await database_session.rollback()
        existing_cart = await _fetch_cart_with_items(
            database_session,
            user_id=user_id,
            session_id=resolved_session_id,
        )
        if existing_cart is not None:
            return existing_cart
        raise

    created_cart = await _fetch_cart_with_items(
        database_session,
        user_id=user_id,
        session_id=resolved_session_id,
    )
    if created_cart is None:
        raise CartServiceError(status_code=500, detail="Failed to load created cart.")
    return created_cart


async def merge_guest_cart(
    database_session: AsyncSession,
    current_user: User,
    guest_session_id: str,
) -> Cart:
    """Idempotently merge a guest session cart into the authenticated user's cart."""
    cleaned_session_id = guest_session_id.strip()
    if not cleaned_session_id:
        raise CartServiceError(
            status_code=400,
            detail="X-Session-Id header is required to merge guest cart.",
        )

    user_cart = await get_or_create_cart(
        database_session,
        current_user=current_user,
        session_id=None,
    )
    guest_cart = await _fetch_cart_with_items(
        database_session,
        user_id=None,
        session_id=cleaned_session_id,
    )
    if guest_cart is None:
        return user_cart

    user_items_by_variant = {
        item.variant_id: item
        for item in user_cart.items
    }

    guest_variant_ids = [item.variant_id for item in guest_cart.items]
    variants_by_id: dict[int, ProductVariant] = {}
    if guest_variant_ids:
        variant_result = await database_session.execute(
            select(ProductVariant).where(ProductVariant.id.in_(guest_variant_ids))
        )
        variants_by_id = {
            variant.id: variant
            for variant in variant_result.scalars().all()
        }

    for guest_item in guest_cart.items:
        variant_record = variants_by_id.get(guest_item.variant_id)
        if variant_record is None or not variant_record.is_active or variant_record.stock <= 0:
            continue

        existing_user_item = user_items_by_variant.get(guest_item.variant_id)
        if existing_user_item is not None:
            merged_quantity = min(
                existing_user_item.quantity + guest_item.quantity,
                variant_record.stock,
            )
            existing_user_item.quantity = merged_quantity
        else:
            capped_quantity = min(guest_item.quantity, variant_record.stock)
            new_item = CartItem(
                cart_id=user_cart.id,
                variant_id=guest_item.variant_id,
                quantity=capped_quantity,
            )
            database_session.add(new_item)

    await database_session.delete(guest_cart)
    await database_session.commit()

    refreshed_cart = await _fetch_cart_with_items(
        database_session,
        user_id=current_user.id,
        session_id=None,
    )
    if refreshed_cart is None:
        raise CartServiceError(status_code=500, detail="Failed to load merged cart.")
    return refreshed_cart


async def clear_cart(
    database_session: AsyncSession,
    current_user: User | None,
    session_id: str | None,
) -> None:
    """Remove all items from the caller's active cart."""
    user_id, resolved_session_id = resolve_cart_owner(current_user, session_id)
    cart_record = await _fetch_cart_with_items(
        database_session,
        user_id=user_id,
        session_id=resolved_session_id,
    )
    if cart_record is None:
        return

    await database_session.execute(
        delete(CartItem).where(CartItem.cart_id == cart_record.id)
    )
    await database_session.commit()
