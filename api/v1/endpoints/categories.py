from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.deps import get_db, require_admin
from models.categories_model import Category
from models.users_model import User
from schemas.categories_schemas import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)
from services import categories_service

router = APIRouter()


def _raise_service_error(service_error: categories_service.CategoryServiceError) -> None:
    raise HTTPException(
        status_code=service_error.status_code,
        detail=service_error.detail,
    ) from service_error


@router.get("/", response_model=list[CategoryResponse])
async def get_all_categories(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    parent_id: int | None = Query(default=None, gt=0),
    active_only: bool = Query(default=True),
    db: AsyncSession = Depends(get_db),
) -> list[Category]:
    """List categories with optional parent and active filters."""
    return await categories_service.list_categories(
        db,
        skip=skip,
        limit=limit,
        parent_id=parent_id,
        active_only=active_only,
    )


@router.get("/slug/{slug}", response_model=CategoryResponse)
async def get_category_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> Category:
    """Get a single category by slug."""
    try:
        return await categories_service.get_category_by_slug(db, slug)
    except categories_service.CategoryServiceError as exc:
        _raise_service_error(exc)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_single_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
) -> Category:
    """Get a single category by ID."""
    try:
        return await categories_service.get_category_by_id(db, category_id)
    except categories_service.CategoryServiceError as exc:
        _raise_service_error(exc)


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    payload: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
) -> Category:
    """Create a new category (admin only)."""
    try:
        return await categories_service.create_category(db, payload)
    except categories_service.CategoryServiceError as exc:
        _raise_service_error(exc)


@router.put("/{category_id}", response_model=CategoryResponse)
async def replace_category(
    category_id: int,
    payload: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
) -> Category:
    """Replace a category completely (admin only)."""
    try:
        return await categories_service.update_category(
            db,
            category_id,
            payload,
            exclude_unset=False,
        )
    except categories_service.CategoryServiceError as exc:
        _raise_service_error(exc)


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
) -> Category:
    """Partially update a category (admin only)."""
    try:
        return await categories_service.update_category(
            db,
            category_id,
            payload,
            exclude_unset=True,
        )
    except categories_service.CategoryServiceError as exc:
        _raise_service_error(exc)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
) -> Response:
    """Delete a category (admin only)."""
    try:
        await categories_service.delete_category(db, category_id)
    except categories_service.CategoryServiceError as exc:
        _raise_service_error(exc)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
