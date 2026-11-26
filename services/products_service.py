from decimal import Decimal
from typing import Literal

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.categories_model import Category
from models.products_model import Product
from schemas.products_schemas import ProductCreate, ProductUpdate

ProductSort = Literal["newest", "price_asc", "price_desc", "rating"]


class ProductServiceError(Exception):
    """Domain error raised by product service operations."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


async def _ensure_category_exists(db: AsyncSession, category_id: int) -> None:
    result = await db.execute(select(Category.id).where(Category.id == category_id))
    if result.scalar_one_or_none() is None:
        raise ProductServiceError(status_code=404, detail="Category not found.")


def _validate_prices(base_price: Decimal, sale_price: Decimal | None) -> None:
    if sale_price is not None and sale_price > base_price:
        raise ProductServiceError(
            status_code=400,
            detail="sale_price cannot exceed base_price.",
        )


async def list_products(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    category_id: int | None = None,
    search: str | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    active_only: bool = True,
    sort_by: ProductSort = "newest",
) -> list[Product]:
    """List products with filtering, search, sorting, and pagination."""
    effective_price = func.coalesce(Product.sale_price, Product.base_price)
    stmt = select(Product)

    if active_only:
        stmt = stmt.where(Product.is_active.is_(True))
    if category_id is not None:
        stmt = stmt.where(Product.category_id == category_id)
    if search:
        term = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                Product.title.ilike(term),
                Product.description.ilike(term),
                Product.fabric.ilike(term),
            )
        )
    if min_price is not None:
        stmt = stmt.where(effective_price >= min_price)
    if max_price is not None:
        stmt = stmt.where(effective_price <= max_price)

    if sort_by == "price_asc":
        stmt = stmt.order_by(effective_price.asc(), Product.id.desc())
    elif sort_by == "price_desc":
        stmt = stmt.order_by(effective_price.desc(), Product.id.desc())
    elif sort_by == "rating":
        stmt = stmt.order_by(Product.rating_avg.desc(), Product.rating_count.desc(), Product.id.desc())
    else:
        stmt = stmt.order_by(Product.created_at.desc(), Product.id.desc())

    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_product_by_id(db: AsyncSession, product_id: int) -> Product:
    """Fetch a single product by ID or raise 404."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if product is None:
        raise ProductServiceError(status_code=404, detail="Product not found.")
    return product


async def get_product_by_slug(db: AsyncSession, slug: str) -> Product:
    """Fetch a single product by slug or raise 404."""
    result = await db.execute(select(Product).where(Product.slug == slug.strip().lower()))
    product = result.scalar_one_or_none()
    if product is None:
        raise ProductServiceError(status_code=404, detail="Product not found.")
    return product


async def create_product(db: AsyncSession, payload: ProductCreate) -> Product:
    """Create a new product after verifying category, slug, and pricing."""
    slug = payload.slug.strip().lower()
    existing = await db.execute(select(Product.id).where(Product.slug == slug))
    if existing.scalar_one_or_none() is not None:
        raise ProductServiceError(
            status_code=409,
            detail="A product with this slug already exists.",
        )

    await _ensure_category_exists(db, payload.category_id)
    _validate_prices(payload.base_price, payload.sale_price)

    product = Product(
        category_id=payload.category_id,
        title=payload.title.strip(),
        slug=slug,
        description=payload.description,
        fabric=payload.fabric.strip() if payload.fabric else None,
        base_price=payload.base_price,
        sale_price=payload.sale_price,
        is_active=payload.is_active,
    )
    db.add(product)
    try:
        await db.commit()
        await db.refresh(product)
    except IntegrityError as exc:
        await db.rollback()
        raise ProductServiceError(
            status_code=409,
            detail="Product conflicts with an existing record.",
        ) from exc
    return product


async def update_product(
    db: AsyncSession,
    product_id: int,
    payload: ProductCreate | ProductUpdate,
    exclude_unset: bool = True,
) -> Product:
    """Update an existing product (supports both PUT and PATCH)."""
    product = await get_product_by_id(db, product_id)
    update_data = payload.model_dump(exclude_unset=exclude_unset)

    if "category_id" in update_data and update_data["category_id"] is not None:
        await _ensure_category_exists(db, update_data["category_id"])

    effective_base = update_data.get("base_price", product.base_price)
    effective_sale = (
        update_data["sale_price"]
        if "sale_price" in update_data
        else product.sale_price
    )
    _validate_prices(effective_base, effective_sale)

    if "slug" in update_data and update_data["slug"] is not None:
        update_data["slug"] = update_data["slug"].strip().lower()
    if "title" in update_data and update_data["title"] is not None:
        update_data["title"] = update_data["title"].strip()
    if "fabric" in update_data and update_data["fabric"] is not None:
        update_data["fabric"] = update_data["fabric"].strip()

    for field, value in update_data.items():
        setattr(product, field, value)

    try:
        await db.commit()
        await db.refresh(product)
    except IntegrityError as exc:
        await db.rollback()
        raise ProductServiceError(
            status_code=409,
            detail="Updated product slug conflicts with an existing product.",
        ) from exc
    return product


async def delete_product(db: AsyncSession, product_id: int) -> None:
    """Delete a product unless referenced by restricted records (e.g., orders)."""
    product = await get_product_by_id(db, product_id)
    await db.delete(product)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise ProductServiceError(
            status_code=409,
            detail="Cannot delete product while order items reference it.",
        ) from exc
