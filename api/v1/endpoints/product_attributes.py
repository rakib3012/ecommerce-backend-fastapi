from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.deps import get_db, require_admin
from models.product_attributes_model import ProductAttribute
from models.users_model import User
from schemas.product_attributes_schemas import (
    ProductAttributeCreate,
    ProductAttributeResponse,
    ProductAttributeUpdate,
)
from services import product_attributes_service

router = APIRouter()


def _raise_service_error(
    service_error: product_attributes_service.ProductAttributeServiceError,
) -> None:
    raise HTTPException(
        status_code=service_error.status_code,
        detail=service_error.detail,
    ) from service_error


@router.get("/", response_model=list[ProductAttributeResponse])
async def get_all_product_attributes(
    product_id: int | None = Query(default=None, gt=0),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    database_session: AsyncSession = Depends(get_db),
) -> list[ProductAttribute]:
    """List product attributes with optional product_id filter."""
    return await product_attributes_service.list_product_attributes(
        database_session,
        product_id=product_id,
        skip=skip,
        limit=limit,
    )


@router.get("/{attribute_id}", response_model=ProductAttributeResponse)
async def get_single_product_attribute(
    attribute_id: int,
    database_session: AsyncSession = Depends(get_db),
) -> ProductAttribute:
    """Get a single product attribute by ID."""
    try:
        return await product_attributes_service.get_product_attribute_by_id(
            database_session,
            attribute_id,
        )
    except product_attributes_service.ProductAttributeServiceError as service_error:
        _raise_service_error(service_error)


@router.post(
    "/",
    response_model=ProductAttributeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product_attribute(
    payload: ProductAttributeCreate,
    database_session: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
) -> ProductAttribute:
    """Create a new product attribute (admin only)."""
    try:
        return await product_attributes_service.create_product_attribute(
            database_session,
            payload,
        )
    except product_attributes_service.ProductAttributeServiceError as service_error:
        _raise_service_error(service_error)


@router.put("/{attribute_id}", response_model=ProductAttributeResponse)
async def replace_product_attribute(
    attribute_id: int,
    payload: ProductAttributeCreate,
    database_session: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
) -> ProductAttribute:
    """Replace a product attribute completely (admin only)."""
    try:
        return await product_attributes_service.update_product_attribute(
            database_session,
            attribute_id,
            payload,
            exclude_unset=False,
        )
    except product_attributes_service.ProductAttributeServiceError as service_error:
        _raise_service_error(service_error)


@router.patch("/{attribute_id}", response_model=ProductAttributeResponse)
async def update_product_attribute(
    attribute_id: int,
    payload: ProductAttributeUpdate,
    database_session: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
) -> ProductAttribute:
    """Partially update a product attribute (admin only)."""
    try:
        return await product_attributes_service.update_product_attribute(
            database_session,
            attribute_id,
            payload,
            exclude_unset=True,
        )
    except product_attributes_service.ProductAttributeServiceError as service_error:
        _raise_service_error(service_error)


@router.delete("/{attribute_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_attribute(
    attribute_id: int,
    database_session: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
) -> Response:
    """Delete a product attribute (admin only)."""
    try:
        await product_attributes_service.delete_product_attribute(
            database_session,
            attribute_id,
        )
    except product_attributes_service.ProductAttributeServiceError as service_error:
        _raise_service_error(service_error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
