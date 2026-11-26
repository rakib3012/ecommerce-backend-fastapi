from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.product_attributes_model import ProductAttribute
from models.products_model import Product
from schemas.product_attributes_schemas import (
    ProductAttributeCreate,
    ProductAttributeUpdate,
)


class ProductAttributeServiceError(Exception):
    """Domain error raised by product attribute service operations."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


async def _ensure_product_exists(
    database_session: AsyncSession,
    product_id: int,
) -> None:
    result = await database_session.execute(
        select(Product.id).where(Product.id == product_id)
    )
    if result.scalar_one_or_none() is None:
        raise ProductAttributeServiceError(status_code=404, detail="Product not found.")


async def list_product_attributes(
    database_session: AsyncSession,
    product_id: int | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[ProductAttribute]:
    """List product attributes with optional product_id filter."""
    statement = select(ProductAttribute)
    if product_id is not None:
        statement = statement.where(ProductAttribute.product_id == product_id)
    statement = (
        statement.order_by(ProductAttribute.display_order.asc(), ProductAttribute.id.asc())
        .offset(skip)
        .limit(limit)
    )
    result = await database_session.execute(statement)
    return list(result.scalars().all())


async def get_product_attribute_by_id(
    database_session: AsyncSession,
    attribute_id: int,
) -> ProductAttribute:
    """Fetch a single product attribute by ID or raise 404."""
    result = await database_session.execute(
        select(ProductAttribute).where(ProductAttribute.id == attribute_id)
    )
    attribute_record = result.scalar_one_or_none()
    if attribute_record is None:
        raise ProductAttributeServiceError(
            status_code=404,
            detail="Product attribute not found.",
        )
    return attribute_record


async def create_product_attribute(
    database_session: AsyncSession,
    payload: ProductAttributeCreate,
) -> ProductAttribute:
    """Create a new product attribute."""
    await _ensure_product_exists(database_session, payload.product_id)

    attribute_record = ProductAttribute(
        product_id=payload.product_id,
        attribute_name=payload.attribute_name.strip(),
        attribute_value=payload.attribute_value.strip(),
        display_order=payload.display_order,
    )
    database_session.add(attribute_record)
    await database_session.commit()
    await database_session.refresh(attribute_record)
    return attribute_record


async def update_product_attribute(
    database_session: AsyncSession,
    attribute_id: int,
    payload: ProductAttributeCreate | ProductAttributeUpdate,
    exclude_unset: bool = True,
) -> ProductAttribute:
    """Update a product attribute (supports PUT and PATCH)."""
    attribute_record = await get_product_attribute_by_id(database_session, attribute_id)
    update_data = payload.model_dump(exclude_unset=exclude_unset, exclude={"product_id"})

    for field_name, field_value in update_data.items():
        if isinstance(field_value, str):
            field_value = field_value.strip()
        setattr(attribute_record, field_name, field_value)

    await database_session.commit()
    await database_session.refresh(attribute_record)
    return attribute_record


async def delete_product_attribute(
    database_session: AsyncSession,
    attribute_id: int,
) -> None:
    """Delete a product attribute."""
    attribute_record = await get_product_attribute_by_id(database_session, attribute_id)
    await database_session.delete(attribute_record)
    await database_session.commit()
