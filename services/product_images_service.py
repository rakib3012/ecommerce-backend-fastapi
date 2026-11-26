from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.product_images_model import ProductImage
from models.product_variants_model import ProductVariant
from models.products_model import Product
from schemas.product_images_schemas import ProductImageCreate, ProductImageUpdate


class ProductImageServiceError(Exception):
    """Domain error raised by product image service operations."""

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
        raise ProductImageServiceError(status_code=404, detail="Product not found.")


async def _ensure_variant_belongs_to_product(
    database_session: AsyncSession,
    product_id: int,
    variant_id: int | None,
) -> None:
    if variant_id is None:
        return
    result = await database_session.execute(
        select(ProductVariant.id).where(
            ProductVariant.id == variant_id,
            ProductVariant.product_id == product_id,
        )
    )
    if result.scalar_one_or_none() is None:
        raise ProductImageServiceError(
            status_code=404,
            detail="Referenced variant does not belong to this product.",
        )


async def _unset_other_primary_images(
    database_session: AsyncSession,
    product_id: int,
    exclude_image_id: int | None = None,
) -> None:
    statement = (
        update(ProductImage)
        .where(
            ProductImage.product_id == product_id,
            ProductImage.is_primary.is_(True),
        )
        .values(is_primary=False)
    )
    if exclude_image_id is not None:
        statement = statement.where(ProductImage.id != exclude_image_id)
    await database_session.execute(statement)


async def list_product_images(
    database_session: AsyncSession,
    product_id: int | None = None,
    variant_id: int | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[ProductImage]:
    """List product images with optional product and variant filters."""
    statement = select(ProductImage)
    if product_id is not None:
        statement = statement.where(ProductImage.product_id == product_id)
    if variant_id is not None:
        statement = statement.where(ProductImage.variant_id == variant_id)
    statement = (
        statement.order_by(
            ProductImage.is_primary.desc(),
            ProductImage.display_order.asc(),
            ProductImage.id.asc(),
        )
        .offset(skip)
        .limit(limit)
    )
    result = await database_session.execute(statement)
    return list(result.scalars().all())


async def get_product_image_by_id(
    database_session: AsyncSession,
    image_id: int,
) -> ProductImage:
    """Fetch a single product image by ID or raise 404."""
    result = await database_session.execute(
        select(ProductImage).where(ProductImage.id == image_id)
    )
    image_record = result.scalar_one_or_none()
    if image_record is None:
        raise ProductImageServiceError(status_code=404, detail="Product image not found.")
    return image_record


async def create_product_image(
    database_session: AsyncSession,
    payload: ProductImageCreate,
) -> ProductImage:
    """Create a product image, enforcing single primary image per product."""
    await _ensure_product_exists(database_session, payload.product_id)
    await _ensure_variant_belongs_to_product(
        database_session,
        payload.product_id,
        payload.variant_id,
    )

    if payload.is_primary:
        await _unset_other_primary_images(database_session, payload.product_id)

    image_record = ProductImage(
        product_id=payload.product_id,
        variant_id=payload.variant_id,
        image_url=payload.image_url.strip(),
        alt_text=payload.alt_text.strip() if payload.alt_text else None,
        display_order=payload.display_order,
        is_primary=payload.is_primary,
    )
    database_session.add(image_record)
    await database_session.commit()
    await database_session.refresh(image_record)
    return image_record


async def update_product_image(
    database_session: AsyncSession,
    image_id: int,
    payload: ProductImageCreate | ProductImageUpdate,
    exclude_unset: bool = True,
) -> ProductImage:
    """Update a product image (supports PUT and PATCH)."""
    image_record = await get_product_image_by_id(database_session, image_id)
    update_data = payload.model_dump(exclude_unset=exclude_unset, exclude={"product_id"})

    if "variant_id" in update_data:
        await _ensure_variant_belongs_to_product(
            database_session,
            image_record.product_id,
            update_data["variant_id"],
        )

    if update_data.get("is_primary") is True:
        await _unset_other_primary_images(
            database_session,
            image_record.product_id,
            exclude_image_id=image_id,
        )

    for field_name, field_value in update_data.items():
        if isinstance(field_value, str):
            field_value = field_value.strip()
        setattr(image_record, field_name, field_value)

    await database_session.commit()
    await database_session.refresh(image_record)
    return image_record


async def delete_product_image(
    database_session: AsyncSession,
    image_id: int,
) -> None:
    """Delete a product image."""
    image_record = await get_product_image_by_id(database_session, image_id)
    await database_session.delete(image_record)
    await database_session.commit()
