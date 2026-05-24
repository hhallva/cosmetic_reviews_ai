from abc import ABC, abstractmethod


class BaseSearchService(ABC):

    @abstractmethod
    def search(
        self,
        product_name: str,
        max_results: int
    ):
        pass