from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ComparisonRequest(BaseModel):
    """Schema for comparing 2 to 4 products (5+ IDs rejected with validation error)."""

    product_ids: list[int] = Field(min_length=2, max_length=4)


class ComparisonSessionResponse(BaseModel):
    """Comparison session response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: str
    user_id: int | None
    product_ids: list[int]
    updated_at: datetime
