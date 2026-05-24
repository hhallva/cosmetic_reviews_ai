from parsers.CosmeticsReviewSearcher import CosmeticsReviewSearcher

if __name__ == "__main__":

    print("===================================")
    print(" AI Cosmetics Review Search System ")
    print("===================================\n")

    # Ввод продукта из консоли
    product_name = input(
        "Введите название косметического продукта: "
    ).strip()

    if not product_name:
        print("[ERROR] Название продукта пустое!")
        exit()

    # Количество результатов
    try:
        max_results = int(
            input("Введите количество результатов (например 5): ")
        )
    except ValueError:
        max_results = 5

    searcher = CosmeticsReviewSearcher()

    reviews = searcher.search_reviews(
        product_name=product_name,
        max_results=max_results
    )

    print("\n===================")
    print(f"Всего найдено: {len(reviews)}")

    # Сохранение
    searcher.save_to_json(
        product_name=product_name,
        data=reviews
    )