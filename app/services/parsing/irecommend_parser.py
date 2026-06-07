from urllib.parse import urlparse, urljoin

from .base_parser import BaseParser
from app.models.review import Review


class IrecommendParser(BaseParser):
    def __init__(self):
        super().__init__(source_name="irecommend", delay=1.5)
        self._visited_urls = set()

    def can_parse(self, url: str) -> bool:
        return "irecommend.ru" in url

    def parse(self, url: str, _depth: int = 0) -> list[Review]:
        """Парсинг страницы irecommend."""
        if _depth > 2 or url in self._visited_urls:
            return []

        self._visited_urls.add(url)
        soup = self.fetch_page(url)
        if not soup:
            return []

        # Проверяем, это список отзывов или конкретный отзыв
        review_list = soup.select("ul.list-comments > li.item")

        if review_list:
            # Это список отзывов
            return self._parse_reviews_list(soup, url, _depth)
        else:
            # Это конкретный отзыв
            return self._parse_single_review(soup, url)

    def _parse_single_review(self, soup, url: str) -> list[Review]:
        """Парсинг конкретного отзыва."""
        # Заголовок
        title_el = soup.select_one("h2.reviewTitle[itemprop='name']") or soup.select_one("h1")
        title = self._safe_text(title_el)

        # Рейтинг
        rating = 0.0
        rating_meta = soup.select_one("meta[itemprop='ratingValue']")
        if rating_meta:
            rating = self._safe_float(rating_meta.get("content"))
        else:
            # Альтернативный способ - считаем включенные звезды
            stars_on = soup.select("div.starsRating div.star div.on")
            if stars_on:
                rating = float(len(stars_on))

        # Текст отзыва
        text_el = soup.select_one("div[itemprop='reviewBody']")
        text = self._safe_text(text_el)

        # Достоинства
        pros = []
        pros_els = soup.select("ul[itemprop='positiveNotes'] li[itemprop='name']")
        for el in pros_els:
            pros.append(self._safe_text(el))

        # Недостатки
        cons = []
        cons_els = soup.select("ul[itemprop='negativeNotes'] li[itemprop='name']")
        for el in cons_els:
            cons.append(self._safe_text(el))

        # Рекомендация
        verdict_el = soup.select_one("div.conclusion span.verdict")
        verdict = self._safe_text(verdict_el)
        recommends = "рекомендует" in verdict.lower() if verdict else None

        if not text or len(text) < 50:
            return []

        # Добавляем достоинства и недостатки в текст
        full_text = text
        if pros:
            full_text += "\n\nДостоинства: " + "; ".join(pros)
        if cons:
            full_text += "\n\nНедостатки: " + "; ".join(cons)
        if recommends is not None:
            full_text += f"\n\n{'Рекомендует' if recommends else 'Не рекомендует'}"

        return [Review(title, full_text, rating, self.source_name, url)]

    def _parse_reviews_list(self, soup, url: str, _depth: int) -> list[Review]:
        """Парсинг списка отзывов."""
        reviews = []

        # Находим все элементы отзывов в списке
        review_items = soup.select("ul.list-comments > li.item")

        for item in review_items:
            # Извлекаем ссылку на полный отзыв
            link_el = item.select_one("a.reviewTextSnippet[href*='/content/']")
            if not link_el:
                continue

            href = link_el.get("href", "")
            if not href:
                continue

            # Формируем полный URL
            full_url = urljoin(url, href)

            # Нормализуем URL
            parsed = urlparse(full_url)
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

            # Пропускаем уже обработанные
            if clean_url in self._visited_urls:
                continue

            # Парсим конкретный отзыв
            try:
                single_reviews = self.parse(clean_url, _depth=_depth + 1)
                reviews.extend(single_reviews)
            except Exception as e:
                print(f"[IRECOMMEND] Error parsing {clean_url}: {e}")
                continue

        return reviews