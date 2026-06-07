class Review:
    def __init__(self, title: str, text: str, rating: float, source: str, url: str):
        self.title = title
        self.text = text
        self.rating = rating
        self.source = source
        self.url = url

    def to_dict(self):
        return {
            "title": self.title,
            "text": self.text,
            "rating": self.rating,
            "source": self.source,
            "url": self.url,
        }

    def __repr__(self):
        return f"Review(title='{self.title[:50]}...', rating={self.rating})"