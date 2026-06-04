from concurrent.futures import ThreadPoolExecutor

from ddgs.ddgs import DDGS

from app.models.search_result import SearchResult
from .base_search_service import BaseSearchService
from .query_builder import QueryBuilder


class DDGSSearchService(BaseSearchService):
    def __init__(self):
        self.query_builder = QueryBuilder()

    def search_single_query(self, query, max_results):
        results_list = []

        try:

            with DDGS() as search:

                results = search.text(
                    query,
                    max_results=max_results
                )

                for item in results:
                    results_list.append(
                        SearchResult(
                            title=item.get("title", ""),
                            url=item.get("href", ""),
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