import re


def normalize(text):
    text = text.lower()
    text = re.sub(r"[^a-zа-я0-9 ]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()