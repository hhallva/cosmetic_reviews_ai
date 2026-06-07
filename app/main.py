from app.services.parsing.parsing_manager import ParsingManager
from app.services.search.search_manager import SearchManager
from app.services.storage.json_storage import JSONStorage

def main():
    product_name = input("Введите продукт: ")

    if not product_name:
        print("[ERROR] Empty product name")
        return

    searcher = SearchManager()

    print("\n[STEP 1] Поиск страниц с отзывами...")
    results = searcher.search(
        product_name=product_name,
        max_results=10
    )
    print(f"[INFO] Найдено страниц: {len(results)}")

    storage = JSONStorage('..\\data')

    if results:
        storage.save_search_results(
            product_name=product_name,
            results=results
        )
    else:
        print("[WARNING] Не удалось найти страницы")

    # print("\n[STEP 2] Парсинг отзывов...")
    # parser = ParsingManager()
    # reviews = parser.parse_search_results(results)
    # print(f"[INFO] Собрано отзывов: {len(reviews)}")
    #
    # if reviews:
    #     storage.save_parsed_reviews(
    #         product_name=product_name,
    #         reviews=reviews
    #     )
    # else:
    #     print("[WARNING] Не удалось распарсить отзывы")

if __name__ == "__main__":
    main()

    # Vivienne Sabo Cabaret Premiere Mascara