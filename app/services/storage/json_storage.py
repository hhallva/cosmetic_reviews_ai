import json
import os

from datetime import datetime


class JSONStorage:

    def __init__(self):
        self.data_folder = "data"
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