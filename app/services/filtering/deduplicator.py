class Deduplicator:

    @staticmethod
    def remove_duplicates(results):
        unique = {}

        for result in results:
            if result.url not in unique:
                unique[result.url] = result

        return list(unique.values())