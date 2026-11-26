from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.deps import get_current_user, get_db, require_admin
from models.orders_model import Order, OrderStatus
from models.users_model import User
from schemas.orders_schemas import OrderCreate, OrderResponse, OrderStatusUpdate
from services import orders_service

router = APIRouter()


def _raise_service_error(
    service_error: orders_service.OrderServiceError,
) -> None:
    raise HTTPException(
        status_code=service_error.status_code,
        detail=service_error.detail,
    ) from service_error


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def place_order(
    payload: OrderCreate,
    database_session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Order:
    """Place an order with server-authoritative totals and row-locked stock deduction."""
    try:
        return await orders_service.create_order(
            database_session,
            payload=payload,
            current_user=current_user,
        )
    except orders_service.OrderServiceError as service_error:
        _raise_service_error(service_error)


@router.get("/", response_model=list[OrderResponse])
async def get_my_orders(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    database_session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Order]:
    """List orders belonging to the authenticated user."""
    return await orders_service.list_user_orders(
        database_session,
        current_user=current_user,
        skip=skip,
        limit=limit,
    )


@router.get("/admin/all", response_model=list[OrderResponse])
async def get_all_orders_admin(
    status_filter: OrderStatus | None = Query(default=None, alias="status"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    database_session: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
) -> list[Order]:
    """List all orders across customers (admin only)."""
    return await orders_service.list_all_orders_admin(
        database_session,
        status_filter=status_filter,
        skip=skip,
        limit=limit,
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_single_order(
    order_id: int,
    database_session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Order:
    """Get a single order by ID (owner or admin)."""
    try:
        return await orders_service.get_order_by_id(
            database_session,
            order_id=order_id,
            current_user=current_user,
        )
    except orders_service.OrderServiceError as service_error:
        _raise_service_error(service_error)


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: int,
    database_session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Order:
    """Cancel an eligible order and restore stock exactly once (owner or admin)."""
    try:
        return await orders_service.cancel_order(
            database_session,
            order_id=order_id,
            current_user=current_user,
        )
    except orders_service.OrderServiceError as service_error:
        _raise_service_error(service_error)


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    database_session: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
) -> Order:
    """Advance or cancel an order lifecycle status (admin only)."""
    try:
        return await orders_service.update_order_status_admin(
            database_session,
            order_id=order_id,
            new_status=payload.status,
            admin_user=admin_user,
        )
    except orders_service.OrderServiceError as service_error:
        _raise_service_error(service_error)
