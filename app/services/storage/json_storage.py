import json
import os

from datetime import datetime


class JSONStorage:

    def __init__(self):
        self.data_folder = "..\\data"
        os.makedirs(self.data_folder, exist_ok=True)

    def save_search_results(self, product_name: str, results):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        safe_name = (
            product_name
            .replace(" ", "_")
            .replace("/", "_")
            .replace("\\", "_")
        )
        filename = (f"{safe_name}_{timestamp}.json")

        filepath = os.path.join(
            self.data_folder,
            filename
        )

        payload = {
            "product_name": product_name,
            "created_at": timestamp,
            "reviews_count": len(results),
            "reviews": [
                result.to_dict()
                for result in results
            ]
        }

        with open(filepath,"w",encoding="utf-8") as file:
            json.dump(
                payload,
                file,
                ensure_ascii=False,
                indent=4
            )

        print(f"\n[SUCCESS] JSON saved:")
        print(filepath)

        return filepath

    def save_parsed_reviews(self, product_name: str, reviews: list):
        """Сохранение распарсенных отзывов."""
        created_at = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        data = {
            "product_name": product_name,
            "created_at": created_at,
            "reviews_count": len(reviews),
            "reviews": [r.to_dict() for r in reviews],
        }

        safe_name = "".join(
            c if c.isalnum() or c in (" ", "-", "_") else "_"
            for c in product_name
        ).strip()

        filename = f"{safe_name}_parsed_{created_at}.json"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"[SAVE] Отзывы сохранены в: {filepath}")
        return filepath