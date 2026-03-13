import json
import os

def load_json(file_name):
    """Wczytuje plik JSON z obsługą błędów."""
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def translate_text(text, src_lang, tgt_lang):
    """Logika tłumaczenia oparta na osnova.json i vuzor.json."""
    if not text.strip():
        return ""

    # Wczytujemy bazy danych
    osnova = load_json('osnova.json')
    vuzor = load_json('vuzor.json')

    # Jeśli tłumaczymy na Prasłowiański (sl)
    if tgt_lang == "sl":
        words = text.split()
        translated_words = []

        for word in words:
            word_lower = word.lower().strip(",.!?:;")
            # Szukamy słowa w Twojej bazie osnova
            # Zakładamy, że osnova to słownik: {"polskie_slowo": "prasłowiański_rdzeń"}
            if word_lower in osnova:
                rdzen = osnova[word_lower]
                
                # Tutaj możesz dodać logikę odmiany korzystając z vuzor.json
                # Na ten moment zwracamy rdzeń z bazy
                translated_words.append(rdzen)
            else:
                # Jeśli nie ma w słowniku, zostawiamy oryginał w nawiasie
                translated_words.append(f"[{word}]")
        
        return " ".join(translated_words)
    
    # Jeśli to inny język, możesz zostawić starego GoogleTranslatora lub info o braku wsparcia
    return "Tłumaczenie wspierane tylko dla języka Prasłowiańskiego (sl)."

def get_languages():
    return {
        "pl": "Polski",
        "sl": "Prasłowiański",
        "en": "Angielski",
        "de": "Niemiecki",
        "ru": "Rosyjski"
    }
