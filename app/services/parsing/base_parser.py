import time
from abc import ABC, abstractmethod

from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from app.models.review import Review


class BaseParser(ABC):
    """Базовый класс парсера отзывов."""
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    def __init__(self, source_name: str, delay: float = 1.0):
        self.source_name = source_name
        self.delay = delay  # Задержка между запросами

    def fetch_page(self, url: str, max_retries: int = 3) -> BeautifulSoup | None:
        """Загрузка страницы с retry логикой."""
        for attempt in range(max_retries):
            try:
                time.sleep(self.delay)

                response = requests.get(
                    url,
                    headers=self.HEADERS,
                    timeout=20
                )
                response.raise_for_status()
                response.encoding = response.apparent_encoding

                return BeautifulSoup(response.text, "html.parser")

            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code if e.response else None

                # 5xx ошибки — серверная проблема, пробуем ещё раз
                if status_code and status_code >= 500:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 2
                        print(f"[PARSER] {url}: {status_code} error, retry in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"[PARSER ERROR] {url}: {e} (after {max_retries} retries)")
                        return None

                # 4xx ошибки — клиентская проблема, не повторяем
                else:
                    print(f"[PARSER ERROR] {url}: {e}")
                    return None

            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"[PARSER] {url}: {e}, retry in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"[PARSER ERROR] {url}: {e} (after {max_retries} retries)")
                    return None

        return None
    @abstractmethod
    def can_parse(self, url: str) -> bool:
        pass

    @abstractmethod
    def parse(self, url: str) -> list[Review]:
        pass

    def _safe_text(self, element, default: str = "") -> str:
        if element is None:
            return default
        return element.get_text(strip=True) or default

    def _safe_float(self, value, default: float = 0.0) -> float:
        try:
            if value is None:
                return default
            return float(str(value).replace(",", ".").strip())
        except (ValueError, TypeError):
            return default