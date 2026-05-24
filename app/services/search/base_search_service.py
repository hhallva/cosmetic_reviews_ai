from abc import ABC, abstractmethod

class BaseSearchService(ABC):

    @abstractmethod
    def search(self, product_name):
        pass