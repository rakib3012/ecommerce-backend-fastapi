from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.deps import get_db, require_admin
from models.product_images_model import ProductImage
from models.users_model import User
from schemas.product_images_schemas import (
    ProductImageCreate,
    ProductImageResponse,
    ProductImageUpdate,
)
from services import product_images_service

router = APIRouter()


def _raise_service_error(
    service_error: product_images_service.ProductImageServiceError,
) -> None:
    raise HTTPException(
        status_code=service_error.status_code,
        detail=service_error.detail,
    ) from service_error


@router.get("/", response_model=list[ProductImageResponse])
async def get_all_product_images(
    product_id: int | None = Query(default=None, gt=0),
    variant_id: int | None = Query(default=None, gt=0),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    database_session: AsyncSession = Depends(get_db),
) -> list[ProductImage]:
    """List product images with optional product and variant filters."""
    return await product_images_service.list_product_images(
        database_session,
        product_id=product_id,
        variant_id=variant_id,
        skip=skip,
        limit=limit,
    )


@router.get("/{image_id}", response_model=ProductImageResponse)
async def get_single_product_image(
    image_id: int,
    database_session: AsyncSession = Depends(get_db),
) -> ProductImage:
    """Get a single product image by ID."""
    try:
        return await product_images_service.get_product_image_by_id(
            database_session,
            image_id,
        )
    except product_images_service.ProductImageServiceError as service_error:
        _raise_service_error(service_error)


@router.post(
    "/",
    response_model=ProductImageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product_image(
    payload: ProductImageCreate,
    database_session: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
) -> ProductImage:
    """Create a new product image (admin only)."""
    try:
        return await product_images_service.create_product_image(
            database_session,
            payload,
        )
    except product_images_service.ProductImageServiceError as service_error:
        _raise_service_error(service_error)


@router.put("/{image_id}", response_model=ProductImageResponse)
async def replace_product_image(
    image_id: int,
    payload: ProductImageCreate,
    database_session: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
) -> ProductImage:
    """Replace a product image completely (admin only)."""
    try:
        return await product_images_service.update_product_image(
            database_session,
            image_id,
            payload,
            exclude_unset=False,
        )
    except product_images_service.ProductImageServiceError as service_error:
        _raise_service_error(service_error)


@router.patch("/{image_id}", response_model=ProductImageResponse)
async def update_product_image(
    image_id: int,
    payload: ProductImageUpdate,
    database_session: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
) -> ProductImage:
    """Partially update a product image (admin only)."""
    try:
        return await product_images_service.update_product_image(
            database_session,
            image_id,
            payload,
            exclude_unset=True,
        )
    except product_images_service.ProductImageServiceError as service_error:
        _raise_service_error(service_error)


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_image(
    image_id: int,
    database_session: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
) -> Response:
    """Delete a product image (admin only)."""
    try:
        await product_images_service.delete_product_image(
            database_session,
            image_id,
        )
    except product_images_service.ProductImageServiceError as service_error:
        _raise_service_error(service_error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
