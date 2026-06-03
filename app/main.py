from app.services.search.search_manager import SearchManager
from app.services.storage.json_storage import JSONStorage

def main():
    product_name = input("Введите продукт: ")

    if not product_name:
        print("[ERROR] Empty product name")
        return

    manager = SearchManager()

    results = manager.search(
        product_name=product_name,
        max_results=5
    )

    print(f"\n[INFO] Найдено: {len(results)}")

    storage = JSONStorage()
    
    storage.save_search_results(
        product_name=product_name,
        results=results
    )

if __name__ == "__main__":
    main()