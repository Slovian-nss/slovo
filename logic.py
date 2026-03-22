import json
import os
import re

class SlovianLogic:
    def __init__(self):
        self.osnova = self._load_json('osnova.json')
        self.vuzor = self._load_json('vuzor.json')
        
        # Reguły fonetyczne (tzw. Sound Laws) - fundament pod ML
        self.sound_laws = [
            (r'ą', 'ǫ'), (r'ę', 'ę'), (r'rz', 'rь'), 
            (r'sz', 'š'), (r'cz', 'č'), (r'ż', 'ž'),
            (r'ć', 'cь'), (r'ś', 'sь'), (r'ź', 'zь'),
            (r'y', 'y'), (r'u', 'u')
        ]

    def _load_json(self, path):
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def get_form(self, vuzor_id, form_type="m1"):
        """Pobiera końcówkę z vuzor.json (domyślnie m1 - mianownik)"""
        pattern = self.vuzor.get(vuzor_id, {})
        return pattern.get(form_type, "")

    def apply_sound_laws(self, word):
        """Rekonstrukcja fonetyczna dla słów spoza bazy"""
        for pattern, replacement in self.sound_laws:
            word = re.sub(pattern, replacement, word)
        
        # Prasłowiański "jer" na końcu, jeśli słowo kończy się spółgłoską
        if re.search(r'[^aeiouyǫęьъ]$', word):
            word += "ъ"
        return word

    def translate_word(self, word):
        # 1. Standaryzacja
        w = word.lower().strip(".,!?:;()")
        if not w: return word

        # 2. Sprawdzenie w bazie osnova.json
        if w in self.osnova:
            entry = self.osnova[w]
            
            # Jeśli wpis jest słownikiem (ma rdzeń i wzorzec)
            if isinstance(entry, dict):
                root = entry.get("osnova", "")
                v_id = entry.get("vuzor", "")
                # Tu w przyszłości AI będzie decydować o 'form_type'
                suffix = self.get_form(v_id, "m1") 
                return root + suffix
            
            # Jeśli wpis to gotowe słowo (string)
            return entry

        # 3. Jeśli słowa nie ma w bazie - 'inteligentna' rekonstrukcja
        return self.apply_sound_laws(w)

    def translate_text(self, text):
        # Rozbijanie na słowa z zachowaniem interpunkcji (prosty regex)
        tokens = re.findall(r"[\w]+|[^\s\w]", text)
        result = []
        for token in tokens:
            if token.isalnum():
                result.append(self.translate_word(token))
            else:
                result.append(token)
        return " ".join(result).replace(" .", ".").replace(" ,", ",")

# Eksport instancji
translator_logic = SlovianLogic()
