from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.categories_model import Category
from schemas.categories_schemas import CategoryCreate, CategoryUpdate


class CategoryServiceError(Exception):
    """Domain error raised by category service operations."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


async def _ensure_parent_exists(db: AsyncSession, parent_id: int | None) -> None:
    if parent_id is None:
        return
    result = await db.execute(select(Category.id).where(Category.id == parent_id))
    if result.scalar_one_or_none() is None:
        raise CategoryServiceError(status_code=404, detail="Parent category not found.")


async def list_categories(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    parent_id: int | None = None,
    active_only: bool = True,
) -> list[Category]:
    """List categories with optional parent and active filters."""
    stmt = select(Category)
    if active_only:
        stmt = stmt.where(Category.is_active.is_(True))
    if parent_id is not None:
        stmt = stmt.where(Category.parent_id == parent_id)
    stmt = stmt.order_by(Category.display_order, Category.id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_category_by_id(db: AsyncSession, category_id: int) -> Category:
    """Fetch a single category by ID or raise 404."""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if category is None:
        raise CategoryServiceError(status_code=404, detail="Category not found.")
    return category


async def get_category_by_slug(db: AsyncSession, slug: str) -> Category:
    """Fetch a single category by slug or raise 404."""
    result = await db.execute(select(Category).where(Category.slug == slug.strip().lower()))
    category = result.scalar_one_or_none()
    if category is None:
        raise CategoryServiceError(status_code=404, detail="Category not found.")
    return category


async def create_category(db: AsyncSession, payload: CategoryCreate) -> Category:
    """Create a new category after checking slug uniqueness and parent existence."""
    slug = payload.slug.strip().lower()
    existing = await db.execute(select(Category.id).where(Category.slug == slug))
    if existing.scalar_one_or_none() is not None:
        raise CategoryServiceError(
            status_code=409,
            detail="A category with this slug already exists.",
        )

    await _ensure_parent_exists(db, payload.parent_id)

    category = Category(
        name=payload.name.strip(),
        slug=slug,
        description=payload.description,
        image_url=payload.image_url,
        parent_id=payload.parent_id,
        display_order=payload.display_order,
        is_active=payload.is_active,
    )
    db.add(category)
    try:
        await db.commit()
        await db.refresh(category)
    except IntegrityError as exc:
        await db.rollback()
        raise CategoryServiceError(
            status_code=409,
            detail="Category conflicts with an existing record.",
        ) from exc
    return category


async def update_category(
    db: AsyncSession,
    category_id: int,
    payload: CategoryCreate | CategoryUpdate,
    exclude_unset: bool = True,
) -> Category:
    """Update an existing category (supports both PUT and PATCH)."""
    category = await get_category_by_id(db, category_id)
    update_data = payload.model_dump(exclude_unset=exclude_unset)

    if "parent_id" in update_data:
        new_parent_id = update_data["parent_id"]
        if new_parent_id == category_id:
            raise CategoryServiceError(
                status_code=400,
                detail="A category cannot be its own parent.",
            )
        await _ensure_parent_exists(db, new_parent_id)

    if "slug" in update_data and update_data["slug"] is not None:
        update_data["slug"] = update_data["slug"].strip().lower()

    if "name" in update_data and update_data["name"] is not None:
        update_data["name"] = update_data["name"].strip()

    for field, value in update_data.items():
        setattr(category, field, value)

    try:
        await db.commit()
        await db.refresh(category)
    except IntegrityError as exc:
        await db.rollback()
        raise CategoryServiceError(
            status_code=409,
            detail="Updated category slug conflicts with an existing category.",
        ) from exc
    return category


async def delete_category(db: AsyncSession, category_id: int) -> None:
    """Delete a category unless referenced by restricted records."""
    category = await get_category_by_id(db, category_id)
    await db.delete(category)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise CategoryServiceError(
            status_code=409,
            detail="Cannot delete category while products reference it.",
        ) from exc
