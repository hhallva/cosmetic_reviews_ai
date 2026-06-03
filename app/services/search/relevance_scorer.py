from app.core.constants import STOP_WORDS
import re
from typing import Any

class RelevanceScorer:
    """
        Класс для оценки релевантности поискового результата по названию товара.

        Использует эвристический скоринг на основе совпадения ключевых слов и
        полного названия. Подходит для быстрой фильтрации/ранжирования
        результатов парсинга, поиска или работы с API.
    """

    @staticmethod
    def normalize(text: str) -> str:
        """
            Приводит текст к единому формату для безопасного сравнения.

            Преобразует строку в нижний регистр и заменяет все символы,
            кроме букв (латиница/кириллица), цифр и пробелов, на пробелы.

            Args:
                text (str): Исходная строка для нормализации.

            Returns:
                str: Нормализованная строка, готовая к поиску/сравнению.

            Example:
                >>> RelevanceScorer.normalize("iPhone 15 Pro Max!!!")
                'iphone 15 pro max '
        """
        text = text.lower()
        return re.sub(r"[^a-zа-я0-9 ]", " ", text)

    def calculate_score(self, product_name: str, result: Any) -> Any:
        """
            Рассчитывает балл релевантности и записывает его в объект результата.

            Логика скоринга:
              +2: за каждое значимое слово из `product_name`, найденное в заголовке или описании (слова из `STOP_WORDS` игнорируются).
              +10: если полное нормализованное название товара найдено целиком.

            Args:
                product_name (str): Название искомого товара.
                result (Any): Объект результата поиска. Должен иметь атрибуты
                            `title` и `description` (строки).

            Returns:
                Any: Тот же объект `result`, но с добавленным/обновлённым атрибутом
                    `keyword_score` (int). Метод мутирует входящий объект на лету.

            Notes:
                • Числа и короткие марки (`15`, `4K`, `XL`, `S`) проходят фильтрацию, так как не входят в `STOP_WORDS`.
                • При необходимости список легко расширяется: `STOP_WORDS |= {'новый', 'buy'}`.
                • Метод не создаёт копию `result` - возвращает ссылку на изменённый объект.
        """
        text = self.normalize(f"{result.title} {result.description}")

        # Фильтруем короткие слова, убирая мусорные совпадения
        keywords = [w for w in self.normalize(product_name).split() 
                    if w and w not in STOP_WORDS]
        
        score = 0

        for word in keywords:
            if word in text:
                score += 2

        if self.normalize(product_name) in text:
            score += 10

        result.keyword_score = score

        return result