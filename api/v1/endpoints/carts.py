from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.deps import get_current_user, get_db, get_optional_current_user
from models.carts_model import Cart
from models.users_model import User
from schemas.carts_schemas import CartResponse
from services import carts_service

router = APIRouter()


def _raise_service_error(service_error: carts_service.CartServiceError) -> None:
    raise HTTPException(
        status_code=service_error.status_code,
        detail=service_error.detail,
    ) from service_error


@router.get("/", response_model=CartResponse)
async def get_my_cart(
    session_id: str | None = Header(default=None, alias="X-Session-Id"),
    database_session: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> Cart:
    """Get or create the caller's active cart (authenticated user or guest session)."""
    try:
        return await carts_service.get_or_create_cart(
            database_session,
            current_user=current_user,
            session_id=session_id,
        )
    except carts_service.CartServiceError as service_error:
        _raise_service_error(service_error)


@router.post("/merge", response_model=CartResponse)
async def merge_guest_cart(
    session_id: str = Header(alias="X-Session-Id"),
    database_session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Cart:
    """Idempotently merge a guest X-Session-Id cart into the authenticated user's cart."""
    try:
        return await carts_service.merge_guest_cart(
            database_session,
            current_user=current_user,
            guest_session_id=session_id,
        )
    except carts_service.CartServiceError as service_error:
        _raise_service_error(service_error)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_my_cart(
    session_id: str | None = Header(default=None, alias="X-Session-Id"),
    database_session: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> Response:
    """Clear all items from the caller's active cart."""
    try:
        await carts_service.clear_cart(
            database_session,
            current_user=current_user,
            session_id=session_id,
        )
    except carts_service.CartServiceError as service_error:
        _raise_service_error(service_error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
