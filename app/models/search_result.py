

class SearchResult:
    def __init__(
        self,
        title: str,
        url: str,
        description: str,
        source: str,
        query: str
    ):

        self.title = title
        self.url = url
        self.description = description
        self.source = source
        self.query = query

        self.keyword_score = 0.0
        self.semantic_score = 0.0
        self.final_score = 0.0

    def to_dict(self):
        return {
            "title": self.title,
            "url": self.url,
            "description": self.description,
            "source": self.source,
            "query": self.query,
            "keyword_score": self.keyword_score,
            "semantic_score": self.semantic_score,
            "final_score": self.final_score
        }