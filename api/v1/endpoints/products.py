from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.deps import get_db, require_admin
from models.products_model import Product
from models.users_model import User
from schemas.products_schemas import ProductCreate, ProductResponse, ProductUpdate
from services import products_service

router = APIRouter()


def _raise_service_error(service_error: products_service.ProductServiceError) -> None:
    raise HTTPException(
        status_code=service_error.status_code,
        detail=service_error.detail,
    ) from service_error


@router.get("/", response_model=list[ProductResponse])
async def get_all_products(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    category_id: int | None = Query(default=None, gt=0),
    search: str | None = Query(default=None, min_length=1, max_length=120),
    min_price: Decimal | None = Query(default=None, ge=0),
    max_price: Decimal | None = Query(default=None, ge=0),
    active_only: bool = Query(default=True),
    sort_by: products_service.ProductSort = Query(default="newest"),
    db: AsyncSession = Depends(get_db),
) -> list[Product]:
    """List products with filtering, search, sorting, and pagination."""
    return await products_service.list_products(
        db,
        skip=skip,
        limit=limit,
        category_id=category_id,
        search=search,
        min_price=min_price,
        max_price=max_price,
        active_only=active_only,
        sort_by=sort_by,
    )


@router.get("/slug/{slug}", response_model=ProductResponse)
async def get_product_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> Product:
    """Get a single product by slug."""
    try:
        return await products_service.get_product_by_slug(db, slug)
    except products_service.ProductServiceError as exc:
        _raise_service_error(exc)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_single_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
) -> Product:
    """Get a single product by ID."""
    try:
        return await products_service.get_product_by_id(db, product_id)
    except products_service.ProductServiceError as exc:
        _raise_service_error(exc)


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    payload: ProductCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
) -> Product:
    """Create a new product (admin only)."""
    try:
        return await products_service.create_product(db, payload)
    except products_service.ProductServiceError as exc:
        _raise_service_error(exc)


@router.put("/{product_id}", response_model=ProductResponse)
async def replace_product(
    product_id: int,
    payload: ProductCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
) -> Product:
    """Replace a product completely (admin only)."""
    try:
        return await products_service.update_product(
            db,
            product_id,
            payload,
            exclude_unset=False,
        )
    except products_service.ProductServiceError as exc:
        _raise_service_error(exc)


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
) -> Product:
    """Partially update a product (admin only)."""
    try:
        return await products_service.update_product(
            db,
            product_id,
            payload,
            exclude_unset=True,
        )
    except products_service.ProductServiceError as exc:
        _raise_service_error(exc)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin), #function-er vitore admin_user use na korleo FastAPI protita request-e route handler chalanor agei Depends(require_admin) execute kore
) -> Response:
    """Delete a product (admin only)."""
    try:
        await products_service.delete_product(db, product_id)
    except products_service.ProductServiceError as exc:
        _raise_service_error(exc)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
