import json
import os
import re


def load_json(file_name):
    """Bezpieczne wczytywanie JSON."""
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_path, file_name)

        if not os.path.exists(full_path):
            return {}

        with open(full_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            return data

        return {}

    except Exception:
        return {}


def translate_word(word, dictionary):
    """Tłumaczy pojedyncze słowo."""
    lower = word.lower()

    if lower in dictionary:
        translated = dictionary[lower]

        if word[0].isupper():
            translated = translated.capitalize()

        return translated

    return word


def translate_text(text, src_lang, tgt_lang):

    if not text.strip():
        return ""

    osnova = load_json("osnova.json")

    if tgt_lang != "sl":
        return "Tłumaczenie dostępne obecnie tylko na Prasłowiański."

    if not osnova:
        return "Błąd: Nie wczytano bazy osnova.json."

    # tokenizacja (obsługuje polskie litery)
    tokens = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)

    result = []

    for token in tokens:

        # interpunkcja
        if re.match(r"[^\w\s]", token):
            result.append(token)
            continue

        translated = translate_word(token, osnova)
        result.append(translated)

    # składanie zdania
    output = ""
    for i, token in enumerate(result):

        if i == 0:
            output += token
            continue

        # brak spacji przed interpunkcją
        if re.match(r"[.,!?;:]", token):
            output += token
        else:
            output += " " + token

    return output


def get_languages():
    return {
        "pl": "Polski",
        "sl": "Prasłowiański",
        "en": "Angielski",
        "de": "Niemiecki",
        "ru": "Rosyjski"
    }
