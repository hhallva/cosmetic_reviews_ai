import shutil
from pathlib import Path
from app.services.dataset_manager import DatasetManager
from app.services.analytics import AnalyticsService

# Очистка старых данных
shutil.rmtree("data/datasets", ignore_errors=True)
Path("data/datasets").mkdir(exist_ok=True)

# Загрузка
manager = DatasetManager("data/datasets")
meta = manager.upload_dataset("D:\\Temp\\Projects\\cosmetic_reviews_ai\\dataset-my.json")
print(f"✅ Загружен: {meta.brand} - {meta.product} ({meta.reviews_count} отзывов)")

# Список
print("\n📋 Все датасеты:")
for m in manager.list_datasets():
    print(f"  [{m.id}] {m.brand} - {m.product} ({m.reviews_count})")

# Аналитика
dataset = manager.get_dataset(meta.id)
analytics = AnalyticsService([dataset])
dashboard = analytics.get_full_dashboard()

print(f"\n📊 Сводка: {dashboard['summary']}")
print(f"😊 Sentiment: {dashboard['sentiment']}")
print(f"🔤 Топ слова: {dashboard['top_words'][:5]}")
print(f"👍 Топ pros: {dashboard['top_pros'][:5]}")
print(f"👎 Топ cons: {dashboard['top_cons'][:5]}")
print(f"📈 По времени: {dashboard['reviews_over_time']}")