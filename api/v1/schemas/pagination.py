from pydantic import BaseModel, Field
from typing import Generic, List, Optional, TypeVar


# Query params
class PageParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

T = TypeVar("T")


# Response envelope (no total by default)
class PageEnvelope(BaseModel, Generic[T]):
    items: List[T]
    page: int
    page_size: int
    has_next: bool


# If you want totals:
class PageEnvelopeWithTotal(PageEnvelope[T]):
    total: int
