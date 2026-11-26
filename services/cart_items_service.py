from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.cart_items_model import CartItem
from models.product_variants_model import ProductVariant
from models.products_model import Product
from models.users_model import User
from schemas.cart_items_schemas import CartItemCreate, CartItemUpdate
from services.carts_service import CartServiceError, get_or_create_cart


class CartItemServiceError(Exception):
    """Domain error raised by cart item service operations."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


async def _get_active_variant(
    database_session: AsyncSession,
    variant_id: int,
) -> ProductVariant:
    result = await database_session.execute(
        select(ProductVariant)
        .join(Product, Product.id == ProductVariant.product_id)
        .where(
            ProductVariant.id == variant_id,
            ProductVariant.is_active.is_(True),
            Product.is_active.is_(True),
        )
    )
    variant_record = result.scalar_one_or_none()
    if variant_record is None:
        raise CartItemServiceError(
            status_code=404,
            detail="Active product variant not found.",
        )
    return variant_record


async def _get_owned_cart_item(
    database_session: AsyncSession,
    cart_item_id: int,
    current_user: User | None,
    session_id: str | None,
) -> CartItem:
    try:
        cart_record = await get_or_create_cart(
            database_session,
            current_user=current_user,
            session_id=session_id,
        )
    except CartServiceError as service_error:
        raise CartItemServiceError(
            status_code=service_error.status_code,
            detail=service_error.detail,
        ) from service_error

    result = await database_session.execute(
        select(CartItem).where(
            CartItem.id == cart_item_id,
            CartItem.cart_id == cart_record.id,
        )
    )
    cart_item_record = result.scalar_one_or_none()
    if cart_item_record is None:
        raise CartItemServiceError(
            status_code=404,
            detail="Cart item not found.",
        )
    return cart_item_record


async def list_cart_items(
    database_session: AsyncSession,
    current_user: User | None,
    session_id: str | None,
) -> list[CartItem]:
    """List all items in the caller's cart."""
    try:
        cart_record = await get_or_create_cart(
            database_session,
            current_user=current_user,
            session_id=session_id,
        )
    except CartServiceError as service_error:
        raise CartItemServiceError(
            status_code=service_error.status_code,
            detail=service_error.detail,
        ) from service_error

    result = await database_session.execute(
        select(CartItem)
        .where(CartItem.cart_id == cart_record.id)
        .order_by(CartItem.id.asc())
    )
    return list(result.scalars().all())


async def add_cart_item(
    database_session: AsyncSession,
    payload: CartItemCreate,
    current_user: User | None,
    session_id: str | None,
) -> CartItem:
    """Add a variant to the caller's cart or increment existing quantity without reserving stock."""
    try:
        cart_record = await get_or_create_cart(
            database_session,
            current_user=current_user,
            session_id=session_id,
        )
    except CartServiceError as service_error:
        raise CartItemServiceError(
            status_code=service_error.status_code,
            detail=service_error.detail,
        ) from service_error

    variant_record = await _get_active_variant(database_session, payload.variant_id)

    existing_result = await database_session.execute(
        select(CartItem).where(
            CartItem.cart_id == cart_record.id,
            CartItem.variant_id == payload.variant_id,
        )
    )
    existing_item = existing_result.scalar_one_or_none()

    new_quantity = (
        existing_item.quantity + payload.quantity
        if existing_item is not None
        else payload.quantity
    )
    if new_quantity > variant_record.stock:
        raise CartItemServiceError(
            status_code=409,
            detail=f"Insufficient stock. Available: {variant_record.stock}.",
        )

    if existing_item is not None:
        existing_item.quantity = new_quantity
        cart_item_record = existing_item
    else:
        cart_item_record = CartItem(
            cart_id=cart_record.id,
            variant_id=payload.variant_id,
            quantity=new_quantity,
        )
        database_session.add(cart_item_record)

    try:
        await database_session.commit()
        await database_session.refresh(cart_item_record)
    except IntegrityError as integrity_error:
        await database_session.rollback()
        raise CartItemServiceError(
            status_code=409,
            detail="Cart item conflicts with an existing item.",
        ) from integrity_error

    return cart_item_record


async def update_cart_item(
    database_session: AsyncSession,
    cart_item_id: int,
    payload: CartItemUpdate,
    current_user: User | None,
    session_id: str | None,
) -> CartItem:
    """Update the quantity of an owned cart item after validating available stock."""
    cart_item_record = await _get_owned_cart_item(
        database_session,
        cart_item_id,
        current_user,
        session_id,
    )
    variant_record = await _get_active_variant(
        database_session,
        cart_item_record.variant_id,
    )

    if payload.quantity > variant_record.stock:
        raise CartItemServiceError(
            status_code=409,
            detail=f"Insufficient stock. Available: {variant_record.stock}.",
        )

    cart_item_record.quantity = payload.quantity
    await database_session.commit()
    await database_session.refresh(cart_item_record)
    return cart_item_record


async def delete_cart_item(
    database_session: AsyncSession,
    cart_item_id: int,
    current_user: User | None,
    session_id: str | None,
) -> None:
    """Remove an owned item from the caller's cart."""
    cart_item_record = await _get_owned_cart_item(
        database_session,
        cart_item_id,
        current_user,
        session_id,
    )
    await database_session.delete(cart_item_record)
    await database_session.commit()
