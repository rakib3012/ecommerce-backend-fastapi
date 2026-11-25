from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    """Shared category fields."""

    name: str = Field(min_length=1, max_length=120)
    slug: str = Field(
        min_length=1,
        max_length=140,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    description: str | None = None
    image_url: str | None = Field(default=None, max_length=500)
    parent_id: int | None = Field(default=None, gt=0)
    display_order: int = Field(default=0, ge=0)
    is_active: bool = True


class CategoryCreate(CategoryBase):
    """Schema for creating a category."""


class CategoryUpdate(BaseModel):
    """Schema for partial updates to an existing category."""

    name: str | None = Field(default=None, min_length=1, max_length=120)
    slug: str | None = Field(
        default=None,
        min_length=1,
        max_length=140,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    description: str | None = None
    image_url: str | None = Field(default=None, max_length=500)
    parent_id: int | None = Field(default=None, gt=0)
    display_order: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class CategoryResponse(CategoryBase):
    """Category response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
