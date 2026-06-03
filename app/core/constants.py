REVIEW_SITES = [
        "otzovik.com",
        "irecommend.ru",
        "wildberries.ru",
        "ozon.ru",
        "makeup.com.ua"
    ]

SEARCH_PATTERNS = [
    '"{product}" отзывы',
    '"{product}" review',
    '"{product}" opinion',
]

STOP_WORDS = frozenset({
        # 🇷🇺 Русские
        'и', 'в', 'во', 'не', 'на', 'с', 'со', 'а', 'о', 'об', 'от', 'до', 'по',
        'из', 'за', 'у', 'к', 'для', 'при', 'без', 'через', 'после', 'чтобы',
        'что', 'как', 'это', 'тот', 'этот', 'такой', 'все', 'ни', 'ли', 'же', 'бы',
        'он', 'она', 'оно', 'они', 'мы', 'вы', 'я', 'ты', 'его', 'ее', 'их',
        'мой', 'твой', 'наш', 'ваш', 'свой', 'сам', 'самый', 'весь', 'каждый',
        # 🇺🇸 Английские
        'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'with', 'by', 'from', 'of', 'is', 'are', 'was', 'were', 'be', 'been',
        'this', 'that', 'these', 'those', 'it', 'its', 'i', 'you', 'he', 'she',
        'we', 'they', 'my', 'your', 'his', 'her', 'our', 'their'
    })


MAX_RESULTS_PER_QUERY: int = 10