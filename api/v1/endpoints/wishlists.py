from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.deps import get_current_user, get_db
from models.users_model import User
from models.wishlists_model import Wishlist
from schemas.wishlists_schemas import WishlistCreate, WishlistResponse
from services import wishlists_service

router = APIRouter()


def _raise_service_error(
    service_error: wishlists_service.WishlistServiceError,
) -> None:
    raise HTTPException(
        status_code=service_error.status_code,
        detail=service_error.detail,
    ) from service_error


@router.get("/", response_model=list[WishlistResponse])
async def get_my_wishlist(
    database_session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Wishlist]:
    """List all wishlist items for the authenticated user."""
    return await wishlists_service.list_wishlist_items(database_session, current_user)


@router.post("/", response_model=WishlistResponse, status_code=status.HTTP_200_OK)
async def add_to_wishlist(
    payload: WishlistCreate,
    database_session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Wishlist:
    """Add a product to the authenticated user's wishlist (duplicate-safe)."""
    try:
        return await wishlists_service.add_to_wishlist(
            database_session,
            payload=payload,
            current_user=current_user,
        )
    except wishlists_service.WishlistServiceError as service_error:
        _raise_service_error(service_error)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_wishlist(
    product_id: int,
    database_session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    """Remove a product from the authenticated user's wishlist."""
    try:
        await wishlists_service.remove_from_wishlist(
            database_session,
            product_id=product_id,
            current_user=current_user,
        )
    except wishlists_service.WishlistServiceError as service_error:
        _raise_service_error(service_error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
