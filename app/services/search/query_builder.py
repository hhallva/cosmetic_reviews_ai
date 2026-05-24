from app.core.constants import REVIEW_SITES, SEARCH_PATTERNS


class QueryBuilder:
    def build_queries(
        self,
        product_name: str
    ):

        queries = []

        for pattern in SEARCH_PATTERNS:

            queries.append(
                pattern.format(
                    product=product_name
                )
            )

        for site in REVIEW_SITES:

            queries.append(
                f'"{product_name}" отзывы site:{site}'
            )

        return queries