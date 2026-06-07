from abc import ABC, abstractmethod

from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from app.models.review import Review


class BaseParser(ABC):
    """Базовый класс парсера отзывов."""

    # Общие заголовки, чтобы не блокировали
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    def __init__(self, source_name: str):
        self.source_name = source_name

    def fetch_page(self, url: str) -> BeautifulSoup | None:
        """Загрузка страницы и возврат BeautifulSoup объекта."""
        try:
            response = requests.get(url, headers=self.HEADERS, timeout=15)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return BeautifulSoup(response.text, "html.parser")
        except Exception as e:
            print(f"[PARSER ERROR] {url}: {e}")
            return None

    @abstractmethod
    def can_parse(self, url: str) -> bool:
        """Проверка, может ли этот парсер обработать URL."""
        pass

    @abstractmethod
    def parse(self, url: str) -> list[Review]:
        """Парсинг страницы. Возвращает список отзывов."""
        pass

    def _safe_text(self, element, default: str = "") -> str:
        """Безопасное извлечение текста из элемента."""
        if element is None:
            return default
        return element.get_text(strip=True) or default

    def _safe_float(self, value, default: float = 0.0) -> float:
        """Безопасное преобразование в float."""
        try:
            if value is None:
                return default
            return float(str(value).replace(",", ".").strip())
        except (ValueError, TypeError):
            return default