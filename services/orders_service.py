from decimal import Decimal
import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.addresses_model import Address
from models.cart_items_model import CartItem
from models.carts_model import Cart
from models.order_items_model import OrderItem
from models.orders_model import (
    DeliveryZone,
    Order,
    OrderStatus,
    PaymentMethod,
    PaymentStatus,
)
from models.product_variants_model import ProductVariant
from models.products_model import Product
from models.users_model import User, UserRole
from schemas.orders_schemas import OrderCreate

DELIVERY_FEE_BY_ZONE: dict[DeliveryZone, Decimal] = {
    DeliveryZone.INSIDE_DHAKA: Decimal("60.00"),
    DeliveryZone.OUTSIDE_DHAKA: Decimal("120.00"),
}

ALLOWED_STATUS_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.PENDING_PAYMENT: {
        OrderStatus.CONFIRMED,
        OrderStatus.PAYMENT_FAILED,
        OrderStatus.CANCELLED,
    },
    OrderStatus.CONFIRMED: {
        OrderStatus.PROCESSING,
        OrderStatus.CANCELLED,
    },
    OrderStatus.PROCESSING: {
        OrderStatus.SHIPPED,
        OrderStatus.CANCELLED,
    },
    OrderStatus.SHIPPED: {
        OrderStatus.DELIVERED,
    },
    OrderStatus.DELIVERED: set(),
    OrderStatus.PAYMENT_FAILED: set(),
    OrderStatus.CANCELLED: set(),
}


class OrderServiceError(Exception):
    """Domain error raised by order service operations."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def _generate_order_number() -> str:
    return f"ORD-{uuid.uuid4().hex[:12].upper()}"


async def _resolve_shipping_snapshot(
    database_session: AsyncSession,
    payload: OrderCreate,
    current_user: User,
) -> dict:
    if payload.address_id is not None:
        address_result = await database_session.execute(
            select(Address).where(
                Address.id == payload.address_id,
                Address.user_id == current_user.id,
            )
        )
        address_record = address_result.scalar_one_or_none()
        if address_record is None:
            raise OrderServiceError(status_code=404, detail="Address not found.")
        return {
            "label": address_record.label,
            "recipient_name": address_record.recipient_name,
            "phone": address_record.phone,
            "street_address": address_record.street_address,
            "area": address_record.area,
            "city": address_record.city,
            "district": address_record.district,
            "postal_code": address_record.postal_code,
            "country": address_record.country,
        }

    if payload.shipping_address_snapshot:
        return payload.shipping_address_snapshot

    raise OrderServiceError(
        status_code=400,
        detail="Either address_id or shipping_address_snapshot is required.",
    )


async def _restore_order_stock_once(
    database_session: AsyncSession,
    order_record: Order,
) -> None:
    if order_record.stock_restored or not order_record.items:
        return

    quantity_by_variant: dict[int, int] = {}
    for order_item in order_record.items:
        quantity_by_variant[order_item.variant_id] = (
            quantity_by_variant.get(order_item.variant_id, 0) + order_item.quantity
        )

    sorted_variant_ids = sorted(quantity_by_variant.keys())
    variants_result = await database_session.execute(
        select(ProductVariant)
        .where(ProductVariant.id.in_(sorted_variant_ids))
        .order_by(ProductVariant.id.asc())
        .with_for_update()
    )
    for variant_record in variants_result.scalars().all():
        variant_record.stock += quantity_by_variant[variant_record.id]

    order_record.stock_restored = True


async def create_order(
    database_session: AsyncSession,
    payload: OrderCreate,
    current_user: User,
) -> Order:
    """Create an order with deterministic SELECT FOR UPDATE stock deduction and server-side totals."""
    shipping_snapshot = await _resolve_shipping_snapshot(
        database_session,
        payload,
        current_user,
    )

    used_user_cart = False
    cart_record: Cart | None = None
    quantity_by_variant: dict[int, int] = {}

    if payload.items:
        for item_input in payload.items:
            quantity_by_variant[item_input.variant_id] = (
                quantity_by_variant.get(item_input.variant_id, 0) + item_input.quantity
            )
    else:
        cart_result = await database_session.execute(
            select(Cart)
            .options(selectinload(Cart.items))
            .where(Cart.user_id == current_user.id)
        )
        cart_record = cart_result.scalar_one_or_none()
        if cart_record is None or not cart_record.items:
            raise OrderServiceError(
                status_code=400,
                detail="Cannot place an order with an empty cart.",
            )
        used_user_cart = True
        for cart_item in cart_record.items:
            quantity_by_variant[cart_item.variant_id] = (
                quantity_by_variant.get(cart_item.variant_id, 0) + cart_item.quantity
            )

    sorted_variant_ids = sorted(quantity_by_variant.keys())

    # Deterministic row-level lock order prevents deadlocks across concurrent checkouts
    variants_result = await database_session.execute(
        select(ProductVariant)
        .where(ProductVariant.id.in_(sorted_variant_ids))
        .order_by(ProductVariant.id.asc())
        .with_for_update()
    )
    variants_by_id = {
        variant_record.id: variant_record
        for variant_record in variants_result.scalars().all()
    }

    missing_variant_ids = [
        variant_id
        for variant_id in sorted_variant_ids
        if variant_id not in variants_by_id
    ]
    if missing_variant_ids:
        raise OrderServiceError(
            status_code=404,
            detail=f"Product variants not found: {missing_variant_ids}",
        )

    product_ids = list({variant.product_id for variant in variants_by_id.values()})
    products_result = await database_session.execute(
        select(Product).where(Product.id.in_(product_ids))
    )
    products_by_id = {
        product_record.id: product_record
        for product_record in products_result.scalars().all()
    }

    subtotal = Decimal("0.00")
    order_items_to_create: list[OrderItem] = []

    for variant_id in sorted_variant_ids:
        variant_record = variants_by_id[variant_id]
        product_record = products_by_id.get(variant_record.product_id)
        requested_quantity = quantity_by_variant[variant_id]

        if (
            product_record is None
            or not product_record.is_active
            or not variant_record.is_active
        ):
            raise OrderServiceError(
                status_code=409,
                detail=f"Variant {variant_record.sku} is no longer available.",
            )

        if variant_record.stock < requested_quantity:
            raise OrderServiceError(
                status_code=409,
                detail=(
                    f"Insufficient stock for SKU {variant_record.sku}. "
                    f"Requested {requested_quantity}, available {variant_record.stock}."
                ),
            )

        if variant_record.price_override is not None:
            unit_price = variant_record.price_override
        elif product_record.sale_price is not None:
            unit_price = product_record.sale_price
        else:
            unit_price = product_record.base_price

        line_total = (unit_price * requested_quantity).quantize(Decimal("0.01"))
        subtotal += line_total

        variant_record.stock -= requested_quantity

        order_items_to_create.append(
            OrderItem(
                product_id=product_record.id,
                variant_id=variant_record.id,
                product_title=product_record.title,
                sku=variant_record.sku,
                size=variant_record.size,
                color=variant_record.color,
                unit_price=unit_price,
                quantity=requested_quantity,
                line_total=line_total,
            )
        )

    discount_amount = Decimal("0.00")
    delivery_fee = DELIVERY_FEE_BY_ZONE[payload.delivery_zone]
    total_amount = (subtotal - discount_amount + delivery_fee).quantize(Decimal("0.01"))

    initial_status = (
        OrderStatus.CONFIRMED
        if payload.payment_method == PaymentMethod.COD
        else OrderStatus.PENDING_PAYMENT
    )

    order_record = Order(
        order_number=_generate_order_number(),
        user_id=current_user.id,
        shipping_address_snapshot=shipping_snapshot,
        delivery_zone=payload.delivery_zone,
        coupon_code=payload.coupon_code.strip() if payload.coupon_code else None,
        subtotal=subtotal,
        discount_amount=discount_amount,
        delivery_fee=delivery_fee,
        total_amount=total_amount,
        payment_method=payload.payment_method,
        payment_status=PaymentStatus.UNPAID,
        status=initial_status,
        stock_restored=False,
        notes=payload.notes.strip() if payload.notes else None,
        items=order_items_to_create,
    )
    database_session.add(order_record)

    if used_user_cart and cart_record is not None:
        await database_session.execute(
            delete(CartItem).where(CartItem.cart_id == cart_record.id)
        )

    await database_session.commit()
    return await get_order_by_id(database_session, order_record.id, current_user)


async def list_user_orders(
    database_session: AsyncSession,
    current_user: User,
    skip: int = 0,
    limit: int = 20,
) -> list[Order]:
    """List orders owned by the authenticated user."""
    result = await database_session.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc(), Order.id.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def list_all_orders_admin(
    database_session: AsyncSession,
    status_filter: OrderStatus | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[Order]:
    """List all orders for admin management with optional status filter."""
    statement = select(Order).options(selectinload(Order.items))
    if status_filter is not None:
        statement = statement.where(Order.status == status_filter)
    statement = (
        statement.order_by(Order.created_at.desc(), Order.id.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await database_session.execute(statement)
    return list(result.scalars().all())


async def get_order_by_id(
    database_session: AsyncSession,
    order_id: int,
    current_user: User,
) -> Order:
    """Fetch a single order by ID, enforcing owner or ADMIN authorization."""
    result = await database_session.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order_id)
    )
    order_record = result.scalar_one_or_none()
    if order_record is None:
        raise OrderServiceError(status_code=404, detail="Order not found.")

    if (
        order_record.user_id != current_user.id
        and current_user.role != UserRole.ADMIN
    ):
        raise OrderServiceError(
            status_code=403,
            detail="You do not have permission to access this order.",
        )
    return order_record


async def cancel_order(
    database_session: AsyncSession,
    order_id: int,
    current_user: User,
) -> Order:
    """Cancel an eligible order and restore stock exactly once."""
    order_record = await get_order_by_id(database_session, order_id, current_user)
    if order_record.status not in {OrderStatus.PENDING_PAYMENT, OrderStatus.CONFIRMED}:
        raise OrderServiceError(
            status_code=409,
            detail=f"Order in status '{order_record.status.value}' cannot be cancelled.",
        )

    order_record.status = OrderStatus.CANCELLED
    await _restore_order_stock_once(database_session, order_record)
    await database_session.commit()
    return await get_order_by_id(database_session, order_id, current_user)


async def update_order_status_admin(
    database_session: AsyncSession,
    order_id: int,
    new_status: OrderStatus,
    admin_user: User,
) -> Order:
    """Enforce server-side order lifecycle transitions and stock restoration."""
    order_record = await get_order_by_id(database_session, order_id, admin_user)
    allowed_next = ALLOWED_STATUS_TRANSITIONS.get(order_record.status, set())
    if new_status not in allowed_next:
        raise OrderServiceError(
            status_code=409,
            detail=(
                f"Invalid order status transition from "
                f"'{order_record.status.value}' to '{new_status.value}'."
            ),
        )

    order_record.status = new_status
    if new_status in {OrderStatus.CANCELLED, OrderStatus.PAYMENT_FAILED}:
        await _restore_order_stock_once(database_session, order_record)

    await database_session.commit()
    return await get_order_by_id(database_session, order_id, admin_user)
