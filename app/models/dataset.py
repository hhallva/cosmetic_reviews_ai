from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Review(BaseModel):
    review_id: int
    author: str
    date: str
    title: str
    rating: Optional[int] = None
    text: str = ""
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)


class Dataset(BaseModel):
    """Единый формат датасета — как на входе, так и на выходе."""
    id: str = Field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))
    source: str
    product: str
    brand: str
    uploaded_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    reviews: list[Review] = Field(default_factory=list)

    @property
    def reviews_count(self) -> int:
        return len(self.reviews)


class DatasetMeta(BaseModel):
    """Метаданные для списка (без отзывов)."""
    id: str
    source: str
    product: str
    brand: str
    uploaded_at: str
    reviews_count: int