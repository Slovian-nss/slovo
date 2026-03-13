import json
import os
import re

def load_json(file_name):
    """Wczytuje plik JSON z gwarancją zwrócenia słownika."""
    try:
        # Pobieramy ścieżkę do katalogu, w którym znajduje się logic.py
        base_path = os.path.dirname(__file__)
        full_path = os.path.join(base_path, file_name)
        
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data is None:
                    return {}
                return data
        return {}
    except Exception as e:
        # W razie błędu zwracamy pusty słownik, żeby .get() nie wywaliło apki
        return {}

def translate_text(text, src_lang, tgt_lang):
    if not text.strip():
        return ""

    # Wczytanie baz - teraz zawsze będą słownikami (pustymi lub nie)
    osnova = load_json('osnova.json')
    vuzor = load_json('vuzor.json')

    if tgt_lang == "sl":
        # Jeśli osnova jest pusta, wyświetlamy komunikat diagnostyczny
        if not osnova:
            return "Błąd: Słownik osnova.json nie został wczytany. Sprawdź czy plik jest w repozytorium."

        # Rozbijanie tekstu na słowa i interpunkcję
        words = re.findall(r"[\w']+|[.,!?;]", text)
        translated_result = []

        for word in words:
            if word in ".,!?;":
                translated_result.append(word)
                continue

            word_lower = word.lower()
            
            # Bezpieczne pobieranie ze słownika
            found_word = osnova.get(word_lower)

            if found_word:
                if word[0].isupper():
                    found_word = found_word.capitalize()
                translated_result.append(found_word)
            else:
                translated_result.append(word) # Jeśli nie ma, zostaw oryginał

        # Składanie zdania
        final_sentence = " ".join(translated_result)
        # Poprawka spacji przed znakami interpunkcyjnymi
        for char in ".,!?;":
            final_sentence = final_sentence.replace(f" {char}", char)
        
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
