from app.core.constants import REVIEW_SITES, SEARCH_PATTERNS
from typing import List

class QueryBuilder:
    """
        Генератор поисковых запросов для сбора информации о товарах.
        
        Формирует набор строк-запросов на основе предопределённых шаблонов
        и списка целевых сайтов-отзовиков. Используется как подготовительный
        этап перед вызовом поисковых сервисов или парсеров.
    """

    def build_queries(self, product_name: str) -> List[str]:
        """
            Создаёт список поисковых запросов для указанного товара.

            Args:
                product_name (str): Название товара, которое подставляется в шаблоны.

            Returns:
                list[str]: Список готовых поисковых строк, содержащий:
                    • Запросы по общим шаблонам из `SEARCH_PATTERNS`.
                    • Запросы по общим шаблонам с оператором `site:` для каждого домена из `REVIEW_SITES`.

            Example:
                >>> builder = QueryBuilder()
                >>> builder.build_queries("Xiaomi 14")
                [
                "купить Xiaomi 14",
                "Xiaomi 14 характеристики",
                "купить Xiaomi 14 site:otzovik.com",
                "купить Xiaomi 14 site:irecommend.ru",
                "Xiaomi 14 характеристики site:otzovik.com",
                "Xiaomi 14 характеристики site:irecommend.ru"
                ]

            Notes:
                • Зависит от глобальных констант `SEARCH_PATTERNS` и `REVIEW_SITES`.
                • Запросы на отзывы автоматически оборачиваются в кавычки для точного совпадения фразы.
                • Не валидирует входную строку: пустой `product_name` вернёт список из "пустых" шаблонов.
        """

        base_queries = [pattern.format(product=product_name) for pattern in SEARCH_PATTERNS]

        site_queries = [
            f"{q} site:{site}"
            for q in base_queries
            for site in REVIEW_SITES
        ]
        
        return base_queries + site_queries