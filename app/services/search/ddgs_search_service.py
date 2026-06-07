import re
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, parse_qs, urlencode

from ddgs.ddgs import DDGS

from app.models.search_result import SearchResult
from .base_search_service import BaseSearchService
from .query_builder import QueryBuilder


class DDGSSearchService(BaseSearchService):
    def __init__(self):
        self.query_builder = QueryBuilder()

        # Паттерны страниц товаров/категорий (не отзывы)
        self.product_url_patterns = [
            "/product/",
            "/catalog/",
            "/dp/",  # Amazon
            "/category/",
            "/shop/",
            "/item/",
        ]

        # Паттерны сайтов-подборок (статьи "10 лучших", не отзывы)
        self.article_patterns = [
            "/article/",
            "/best-",
            "/top-",
            "/10-",
            "-review",  # Единичные обзоры типа "mascara-review"
        ]

        # Чёрный список доменов (спам, нерелевант, зеркала, кэш, подборки)
        self.blacklisted_domains = [
            "tripadvisor.com",
            "yourvougesnikestore.com",
            "web.archive.org",           # Кэш — дублирует оригинал
            "irecommend.reviews",        # Зеркало irecommend
            "swizzlecms.com",            # Сайт-подборка
            "thegoodmotherproject.com",  # Сайт-подборка
            "vampyvarnish.com",          # Сайт-подборка
            "pinterest.com",             # Пины с картинками, не отзывы
            "tiktok.com",                # Видео, не текстовые отзывы
            "youtube.com",               # Видео, не текстовые отзывы
        ]


        # Параметры URL, которые нужно игнорировать при нормализации
        self.ignored_query_params = {
            'page', 'p', 'pg', 'offset',  # Пагинация
            'new', 'rate', 'sort',  # Сортировка/фильтры
            'order', 'filter', 'from',  # Фильтры
            'utm_source', 'utm_medium',  # UTM-метки
            'utm_campaign', 'utm_content',
            'utm_term', 'ref', 'from_market',
        }

    def _is_valid_url(self, url: str) -> bool:
        """Проверка, что URL валидный и не мусорный."""
        if not url or not isinstance(url, str):
            return False

        url = url.strip()

        if not url.startswith(("http://", "https://")):
            return False

        try:
            parsed = urlparse(url)
            hostname = (parsed.hostname or "").lower()
            path = parsed.path.lower()

            # Отбрасываем рекламные редиректы
            if "bing.com" in hostname and "/aclick" in url:
                return False
            if "google." in hostname and "/url?" in url:
                return False

            # Отбрасываем чёрный список доменов
            if any(domain in hostname for domain in self.blacklisted_domains):
                return False

            # Отбрасываем страницы товаров/категорий
            if any(pattern in path for pattern in self.product_url_patterns):
                return False

            # Отбрасываем сайты-подборки (статьи)
            if any(pattern in path for pattern in self.article_patterns):
                return False

            return True
        except Exception:
            return False

    def _is_valid_result(self, item: dict) -> bool:
        """Проверка, что результат не пустой и имеет смысл."""
        title = (item.get("title") or "").strip()
        description = (item.get("body") or "").strip()
        url = (item.get("href") or "").strip()

        if not title and not description and not url:
            return False

        if not description:
            return False

        if not self._is_valid_url(url):
            return False

        return True

    def _normalize_url(self, url: str) -> str:
        """Умная нормализация URL для дедупликации с учётом домена."""
        try:
            parsed = urlparse(url)
            hostname = (parsed.hostname or "").lower()
            path = parsed.path

            # === irecommend.ru ===
            # Убираем page, new, rate, sort — это пагинация/сортировка одной темы
            if "irecommend.ru" in hostname:
                query_params = parse_qs(parsed.query)
                filtered_params = {
                    k: v for k, v in query_params.items()
                    if k.lower() not in {
                        'page', 'p', 'pg', 'new', 'rate',
                        'sort', 'order', 'from', 'offset'
                    }
                }
                normalized_query = urlencode(filtered_params, doseq=True)
                return parsed._replace(query=normalized_query).geturl()

            # === otzovik.com ===
            # /reviews/.../11/ → /reviews/.../ (убираем номер страницы)
            # /review_XXXXX.html → оставляем как есть (конкретный отзыв)
            if "otzovik.com" in hostname:
                if "/reviews/" in path:
                    parts = [p for p in path.split("/") if p]
                    if parts and parts[-1].isdigit():
                        parts = parts[:-1]
                    path = "/" + "/".join(parts) + "/"
                    return f"{parsed.scheme}://{parsed.netloc}{path}"
                # Для конкретных отзывов — только UTM
                query_params = parse_qs(parsed.query)
                filtered_params = {
                    k: v for k, v in query_params.items()
                    if k.lower() not in self.ignored_query_params
                }
                normalized_query = urlencode(filtered_params, doseq=True)
                return parsed._replace(query=normalized_query).geturl()

            # === kosmetista.ru ===
            # Убираем /pageX/ из path
            if "kosmetista.ru" in hostname:
                path = re.sub(r'/page\d+/', '/', path)
                return parsed._replace(path=path, query="").geturl()

            # === По умолчанию ===
            # Только UTM-метки
            query_params = parse_qs(parsed.query)
            filtered_params = {
                k: v for k, v in query_params.items()
                if k.lower() not in self.ignored_query_params
            }
            normalized_query = urlencode(filtered_params, doseq=True)
            return parsed._replace(query=normalized_query).geturl()

        except Exception:
            return url

    def search_single_query(self, query, max_results):
        results_list = []

        try:

            with DDGS() as search:
                results = search.text(
                    query,
                    max_results=max_results
                )

                for item in results:
                    if not self._is_valid_result(item):
                        continue

                    results_list.append(
                        SearchResult(
                            title=item.get("title", ""),
                            url=self._normalize_url(item.get("href", "")),
                            description=item.get("body", ""),
                            source="ddgs",
                            query=query
                        )
                    )

        except Exception as e:

            print(f"[ERROR] {query}: {e}")

        return results_list

    def search(
            self,
            product_name,
            max_results=10
    ):
        queries = self.query_builder.build_queries(
            product_name
        )

        all_results = []

        with ThreadPoolExecutor(
                max_workers=len(queries)
        ) as executor:
            futures = [
                executor.submit(
                    self.search_single_query,
                    query,
                    max_results
                )

                for query in queries
            ]

            for future in futures:
                all_results.extend(
                    future.result()
                )

        return all_results