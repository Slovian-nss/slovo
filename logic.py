import json
import os
import re

def load_json(file_name):
    """Wczytuje plik JSON z aktualnego katalogu roboczego."""
    try:
        # Streamlit Cloud czasem wymaga pełnej ścieżki
        base_path = os.path.dirname(__file__)
        full_path = os.path.join(base_path, file_name)
        
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception:
        return {}

def translate_text(text, src_lang, tgt_lang):
    if not text.strip():
        return ""

    # 1. Wczytanie baz danych
    osnova = load_json('osnova.json')
    vuzor = load_json('vuzor.json')

    # Jeśli baza jest pusta, zwróć informację debugującą
    if not osnova:
        return "Błąd: Nie znaleziono pliku osnova.json lub plik jest pusty."

    # 2. Logika dla języka Prasłowiańskiego
    if tgt_lang == "sl":
        # Rozdzielamy tekst na słowa, zachowując znaki interpunkcyjne
        words = re.findall(r"[\w']+|[.,!?;]", text)
        translated_result = []

        for word in words:
            # Sprawdzamy, czy to znak interpunkcyjny
            if word in ".,!?;":
                translated_result.append(word)
                continue

            # Szukanie w słowniku (małymi literami)
            word_lower = word.lower()
            
            # PROSTY MECHANIZM DOPASOWANIA
            # Zakładamy strukturę osnova.json: {"matka": "mati", "jest": "estъ", "kościół": "crьky"}
            found_word = osnova.get(word_lower)

            if found_word:
                # Zachowanie wielkości liter (jeśli oryginał był z dużej, wynik też)
                if word[0].isupper():
                    found_word = found_word.capitalize()
                translated_result.append(found_word)
            else:
                # Jeśli słowa nie ma w słowniku, zwracamy je w gwiazdkach (do debugowania)
                translated_result.append(f"*{word}*")

        # Łączenie słów (poprawka spacji przed interpunkcją)
        final_sentence = " ".join(translated_result)
        final_sentence = final_sentence.replace(" .", ".").replace(" ,", ",").replace(" ?", "?")
        
        return final_sentence

    return "Tłumaczenie dostępne tylko na Prasłowiański."

def get_languages():
    return {
        "pl": "Polski",
        "sl": "Prasłowiański",
        "en": "Angielski",
        "de": "Niemiecki",
        "ru": "Rosyjski"
    }
