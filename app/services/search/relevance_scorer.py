import re


class RelevanceScorer:

    @staticmethod
    def normalize(text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^a-zа-я0-9 ]"," ",text)
        return text

    def calculate_score(self, product_name: str, result):

        text = self.normalize(f"{result.title} {result.description}")
        keywords = self.normalize(product_name).split()
        score = 0

        for word in keywords:
            if word in text:
                score += 2

        if self.normalize(product_name) in text:
            score += 10

        result.keyword_score = score

        return result