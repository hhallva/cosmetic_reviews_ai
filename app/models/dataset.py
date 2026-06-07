from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DatasetInfo(BaseModel):
    source: str = "unknown"


class Product(BaseModel):
    name: str
    brand: str


class Review(BaseModel):
    review_id: int
    author: str
    date: str
    title: str
    rating: Optional[int] = None
    text: str = ""
    pros: list[str] = []
    cons: list[str] = []


class Dataset(BaseModel):
    id: str = Field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))
    name: str
    source: str
    product_name: str
    brand: str
    uploaded_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    reviews_count: int = 0
    file_path: str = ""
    reviews: list[Review] = []


class DatasetMeta(BaseModel):
    """Метаданные датасета (без самих отзывов — для списка)."""
    id: str
    name: str
    source: str
    product_name: str
    brand: str
    uploaded_at: str
    reviews_count: int