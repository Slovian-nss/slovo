import json
import os
import re

class SlovianLogic:
    def __init__(self, osnova_path='osnova.json', vuzor_path='vuzor.json'):
        self.osnova = self._load(osnova_path)
        self.vuzor  = self._load(vuzor_path)
        self.rules = {
            'ą': 'ǫ',  'ę': 'ę',   'rz': 'rь', 'sz': 'š',
            'cz': 'č', 'ż': 'ž',   'ć': 'cь', 'ś': 'sь'
        }

    def _load(self, path):
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def get_base_form(self, polish_lower):
        for entry in self.osnova:
            if entry.get("polish", "").lower() == polish_lower:
                return entry.get("slovian", None)
        return None

    def get_declension(self, slovian_base, vuzor_id=None, case="nominative", number="singular"):
        if not slovian_base:
            return None

        # Najpierw szukamy dokładnego dopasowania słowiańskiego słowa
        for entry in self.vuzor:
            if entry.get("slovian", "").lower() == slovian_base.lower():
                key = entry.get("type and case", "").lower()
                if "nominative" in key and "singular" in key:
                    return entry.get("slovian")

        # Jeśli nie ma – fallback na vuzor_id (jeśli był w osnova)
        if vuzor_id:
            for entry in self.vuzor:
                slov = entry.get("slovian", "").lower()
                if slov.startswith(slovian_base.lower()) and case.lower() in entry["type and case"].lower():
                    if number.lower() in entry["type and case"].lower():
                        return entry["slovian"]

        return slovian_base  # ostateczny fallback

    def translate_word(self, word):
        original = word
        clean = word.lower().strip(".,!?;:")

        # 1. Szukamy dokładnego polskiego → słowiańskie
        slov_base = self.get_base_form(clean)
        if slov_base:
            # Tu można dodać logikę przypadku, na razie baza
            return slov_base

        # 2. Rekonstrukcja fonetyczna
        recon = clean
        for pl, sl in self.rules.items():
            recon = recon.replace(pl, sl)

        if recon and recon[-1] not in "aeiouyęǫьъ":
            recon += "ъ"

        return recon

    def translate_sentence(self, text):
        if not text.strip():
            return "(ne najdeno teksta)"

        # Zachowujemy interpunkcję i wielkość liter
        words = re.findall(r"(\w+|[^\w\s])", text)
        result = []

        for token in words:
            if token.isspace() or not token.strip(".,!?;:"):
                result.append(token)
                continue

            translated = self.translate_word(token)
            # Przymiotniki przed rzeczownikami – na razie bez analizy składniowej
            result.append(translated)

        return "".join(result).replace("  ", " ").strip()
