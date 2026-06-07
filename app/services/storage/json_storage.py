import json
import os

from datetime import datetime


class JSONStorage:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def save_search_results(self, product_name: str, results):
        created_at = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        data = {
            "product_name": product_name,
            "created_at": created_at,
            "reviews_count": len(results),
            "reviews": [r.to_dict() for r in results],
        }

        safe_name = "".join(
            c if c.isalnum() or c in (" ", "-", "_") else "_"
            for c in product_name
        ).strip()

        filename = f"{safe_name}_{created_at}.json"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"[SUCCESS] JSON saved: {filepath}")
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

        print(f"[SUCCESS] Parsed reviews saved: {filepath}")
        return filepath