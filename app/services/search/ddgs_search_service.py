from ddgs.ddgs import DDGS

from app.models.search_result import SearchResult
from .base_search_service import BaseSearchService
from .query_builder import QueryBuilder


class DDGSSearchService(BaseSearchService):
     
    def __init__(self):
        self.query_builder = QueryBuilder()

    def search(self, product_name: str, max_results: int = 10):

        all_results = []

        queries = self.query_builder.build_queries(
            product_name
        )

        with DDGS() as search:
            for query in queries:
                print(f"[INFO] {query}")

                try:
                    results = search.text(
                        query,
                        max_results=max_results
                    )

                    results = list(results)

                    for item in results:
                        search_result = SearchResult(
                            title=item.get("title", ""),
                            url=item.get("href", ""),
                            description=item.get("body", ""),
                            source="ddgs",
                            query=query
                        )

                        all_results.append(
                            search_result
                        )

                except Exception as e:
                    print(f"[ERROR] {e}")

        return all_results