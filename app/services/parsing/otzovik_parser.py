from urllib.parse import urljoin, urlparse, parse_qs, urlencode

from .base_parser import BaseParser
from app.models.review import Review


class OtzovikParser(BaseParser):
    def __init__(self):
        super().__init__(source_name="otzovik", delay=2.0)

    def can_parse(self, url: str) -> bool:
        return "otzovik.com" in url

    def parse(self, url: str) -> list[Review]:
        """Парсинг страницы otzovik."""
        soup = self.fetch_page(url)
        if not soup:
            return []

        # Проверяем тип страницы
        if "/review_" in url and url.endswith(".html"):
            # Конкретный отзыв
            return self._parse_single_review(soup, url)
        elif "/reviews/" in url:
            # Список отзывов - парсим и позитивные, и негативные
            return self._parse_reviews_list_with_ratios(url)

        return []

    def _parse_single_review(self, soup, url: str) -> list[Review]:
        """Парсинг конкретного отзыва."""
        # Заголовок
        title_el = soup.select_one("h1[itemprop='name']") or soup.select_one("h1")
        title = self._safe_text(title_el)

        # Рейтинг
        rating_el = soup.select_one("span[itemprop='ratingValue']")
        rating = self._safe_float(rating_el)

        # Текст отзыва
        text_el = soup.select_one("div[itemprop='reviewBody']")
        if not text_el:
            text_el = soup.select_one(".review-body") or soup.select_one(".body-review")
        text = self._safe_text(text_el)

        if not text or len(text) < 50:
            return []

        return [Review(title, text, rating, self.source_name, url)]

    def _parse_reviews_list_with_ratios(self, base_url: str) -> list[Review]:
        """Парсинг списка отзывов с учетом позитивных и негативных."""
        all_reviews = []

        # Парсим базовую страницу
        reviews = self._parse_reviews_list_page(base_url)
        all_reviews.extend(reviews)

        # Парсим позитивные отзывы (?ratio=Y)
        positive_url = self._add_ratio_param(base_url, "Y")
        if positive_url != base_url:
            reviews = self._parse_reviews_list_page(positive_url)
            all_reviews.extend(reviews)

        # Парсим негативные отзывы (?ratio=N)
        negative_url = self._add_ratio_param(base_url, "N")
        if negative_url != base_url:
            reviews = self._parse_reviews_list_page(negative_url)
            all_reviews.extend(reviews)

        return all_reviews

    def _add_ratio_param(self, url: str, ratio: str) -> str:
        """Добавляет параметр ratio к URL."""
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        query_params['ratio'] = [ratio]
        new_query = urlencode(query_params, doseq=True)
        return parsed._replace(query=new_query).geturl()

    def _parse_reviews_list_page(self, url: str) -> list[Review]:
        """Парсинг одной страницы списка отзывов."""
        soup = self.fetch_page(url)
        if not soup:
            return []

        reviews = []

        # Ищем ссылки на конкретные отзывы
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

            # Парсим каждый отзыв
            single_reviews = self.parse(full_url)
            reviews.extend(single_reviews)

        return reviews