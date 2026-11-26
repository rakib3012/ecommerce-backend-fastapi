from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.deps import get_db, get_optional_current_user
from models.cart_items_model import CartItem
from models.users_model import User
from schemas.cart_items_schemas import (
    CartItemCreate,
    CartItemResponse,
    CartItemUpdate,
)
from services import cart_items_service

router = APIRouter()


def _raise_service_error(
    service_error: cart_items_service.CartItemServiceError,
) -> None:
    raise HTTPException(
        status_code=service_error.status_code,
        detail=service_error.detail,
    ) from service_error


@router.get("/", response_model=list[CartItemResponse])
async def get_cart_items(
    session_id: str | None = Header(default=None, alias="X-Session-Id"),
    database_session: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> list[CartItem]:
    """List all items in the caller's active cart."""
    try:
        return await cart_items_service.list_cart_items(
            database_session,
            current_user=current_user,
            session_id=session_id,
        )
    except cart_items_service.CartItemServiceError as service_error:
        _raise_service_error(service_error)


@router.post(
    "/",
    response_model=CartItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_cart_item(
    payload: CartItemCreate,
    session_id: str | None = Header(default=None, alias="X-Session-Id"),
    database_session: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> CartItem:
    """Add a product variant to the caller's cart (or increment quantity)."""
    try:
        return await cart_items_service.add_cart_item(
            database_session,
            payload=payload,
            current_user=current_user,
            session_id=session_id,
        )
    except cart_items_service.CartItemServiceError as service_error:
        _raise_service_error(service_error)


@router.patch("/{cart_item_id}", response_model=CartItemResponse)
async def update_cart_item(
    cart_item_id: int,
    payload: CartItemUpdate,
    session_id: str | None = Header(default=None, alias="X-Session-Id"),
    database_session: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> CartItem:
    """Update quantity for an item in the caller's cart."""
    try:
        return await cart_items_service.update_cart_item(
            database_session,
            cart_item_id=cart_item_id,
            payload=payload,
            current_user=current_user,
            session_id=session_id,
        )
    except cart_items_service.CartItemServiceError as service_error:
        _raise_service_error(service_error)


@router.delete("/{cart_item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cart_item(
    cart_item_id: int,
    session_id: str | None = Header(default=None, alias="X-Session-Id"),
    database_session: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> Response:
    """Remove an item from the caller's cart."""
    try:
        await cart_items_service.delete_cart_item(
            database_session,
            cart_item_id=cart_item_id,
            current_user=current_user,
            session_id=session_id,
        )
    except cart_items_service.CartItemServiceError as service_error:
        _raise_service_error(service_error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
