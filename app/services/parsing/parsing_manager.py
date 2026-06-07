from concurrent.futures import ThreadPoolExecutor, as_completed
from app.services.parsing.otzovik_parser import OtzovikParser
from app.services.parsing.irecommend_parser import IrecommendParser


class ParsingManager:
    def __init__(self):
        self.parsers = [
            OtzovikParser(),
            IrecommendParser(),
        ]

    def _get_parser(self, url: str):
        for parser in self.parsers:
            if parser.can_parse(url):
                return parser
        return None

    def parse_url(self, url: str) -> list:
        parser = self._get_parser(url)
        if not parser:
            print(f"[PARSER] No parser for URL: {url}")
            return []

        try:
            reviews = parser.parse(url)
            if reviews:
                print(f"[PARSER] ✓ {url}: {len(reviews)} reviews")
            else:
                print(f"[PARSER] ✗ {url}: 0 reviews")
            return reviews
        except Exception as e:
            print(f"[PARSER ERROR] {url}: {e}")
            return []

    def parse_urls(self, urls: list[str], max_workers: int = 3) -> list:
        """Параллельный парсинг с уменьшенным количеством воркеров."""
        all_reviews = []

        # Используем меньше воркеров, чтобы не перегружать сайты
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(self.parse_url, url): url
                for url in urls
            }

            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    reviews = future.result()
                    all_reviews.extend(reviews)
                except Exception as e:
                    print(f"[PARSER ERROR] {url}: {e}")

        return all_reviews

    def parse_search_results(self, search_results) -> list:
        urls = [result.url for result in search_results]
        return self.parse_urls(urls)