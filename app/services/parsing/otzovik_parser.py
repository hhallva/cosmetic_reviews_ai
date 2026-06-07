from urllib.parse import urljoin

from .base_parser import BaseParser
from app.models.review import Review


class OtzovikParser(BaseParser):
    def __init__(self):
        super().__init__(source_name="otzovik", delay=2.0)

    def can_parse(self, url: str) -> bool:
        return "otzovik.com" in url

    def parse(self, url: str) -> list[Review]:
        soup = self.fetch_page(url)
        if not soup:
            return []

        # Определяем тип страницы
        if "/review_" in url and url.endswith(".html"):
            # Конкретный отзыв
            return self._parse_single_review(soup, url)
        elif "/reviews/" in url:
            # Список отзывов — собираем ссылки и парсим каждый
            return self._parse_reviews_list(soup, url)

        return []

    def _parse_single_review(self, soup, url: str) -> list[Review]:
        reviews = []

        title_el = soup.select_one("h1[itemprop='name']") or soup.select_one("h1")
        title = self._safe_text(title_el)

        rating_el = soup.select_one("span[itemprop='ratingValue']")
        rating = self._safe_float(rating_el)

        text_el = soup.select_one("div[itemprop='reviewBody']")
        if not text_el:
            text_el = soup.select_one(".review-body") or soup.select_one(".body-review")
        text = self._safe_text(text_el)

        if title or text:
            reviews.append(Review(title, text, rating, self.source_name, url))

        return reviews

    def _parse_reviews_list(self, soup, url: str) -> list[Review]:
        reviews = []
        links = soup.select("a[href*='/review_']")
        seen_urls = set()

        for link in links:
            href = link.get("href", "")
            if not href or "/review_" not in href:
                continue

            full_url = urljoin(url, href).split("#")[0]

            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)

            single_reviews = self.parse(full_url)
            reviews.extend(single_reviews)

        return reviews