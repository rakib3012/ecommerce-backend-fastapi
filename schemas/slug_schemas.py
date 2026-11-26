from enum import Enum

from pydantic import BaseModel, Field


class SlugTargetType(str, Enum):
    """Supported entities that own unique URL slugs."""

    CATEGORY = "category"
    PRODUCT = "product"


class SlugGenerateRequest(BaseModel):
    """Request payload for generating a unique slug from text."""

    text: str = Field(min_length=1, max_length=220)
    target_type: SlugTargetType = SlugTargetType.PRODUCT


class SlugGenerateResponse(BaseModel):
    """Generated slug and availability status."""

    slug: str
    is_available: bool


class SlugAvailabilityResponse(BaseModel):
    """Slug availability check result."""

    slug: str
    target_type: SlugTargetType
    is_available: bool


class SlugLookupResponse(BaseModel):
    """Resolved entity metadata for a storefront slug lookup."""

    target_type: SlugTargetType
    target_id: int
    slug: str
    title: str
