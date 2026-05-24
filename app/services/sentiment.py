from utils.text_utils import normalize

def calculate_relevance(product_name, item):
    text = normalize(f"{item["title"]} {item["description"]}")

    keywords = normalize(product_name).split()
    score = 0

    for word in keywords:
        if word in text:
            score += 3

    #Точное совпадение
    if normalize(product_name) in text:
        score += 15

    #Бонус за URL
    if "review" in item["url"]:
        score += 5

    if "otziv" in item["url"]:
        score += 5

    return score