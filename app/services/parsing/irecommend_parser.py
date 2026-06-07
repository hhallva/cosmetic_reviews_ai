from .base_parser import BaseParser
from app.models.review import Review

class IrecommendParser(BaseParser):
    def __init__(self):
        super().__init__(source_name="irecommend", delay=1.5)

    def can_parse(self, url: str) -> bool:
        return "irecommend.ru" in url

    def parse(self, url: str) -> list[Review]:
        soup = self.fetch_page(url)
        if not soup:
            return []

        title_el = (
            soup.select_one("h1[itemprop='name']")
            or soup.select_one(".b-review-header__title")
            or soup.select_one("h1")
        )
        title = self._safe_text(title_el)

        rating_el = soup.select_one("span[itemprop='ratingValue']")
        rating = self._safe_float(rating_el)

        text_el = (
            soup.select_one("div[itemprop='reviewBody']")
            or soup.select_one(".b-review__body")
        )
        text = self._safe_text(text_el)

        if title or text:
            return [Review(title, text, rating, self.source_name, url)]

        return []