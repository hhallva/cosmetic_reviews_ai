from app.services.search.ddgs_search_service import DDGSSearchService
from app.services.search.relevance_scorer import RelevanceScorer
from app.services.filtering.deduplicator import Deduplicator

class SearchManager:
    def __init__(self):
        self.search_service = DDGSSearchService()
        self.relevance_scorer = RelevanceScorer()

    def search(
        self,
        product_name,
        max_results=10
    ):

        results = self.search_service.search(product_name,max_results)
        results = Deduplicator.remove_duplicates(results)

        for result in results:
            self.relevance_scorer.calculate_score(product_name,result)

        results.sort(
            key=lambda x: x.keyword_score,
            reverse=True
        )

        return results