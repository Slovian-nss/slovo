import json
from typing import Dict, Tuple, Optional

class SlovianDecliner:
    def __init__(self):
        with open('vuzor.json', encoding='utf-8') as f:
            self.vuzor = json.load(f)
        self.lookup: Dict[Tuple[str, str], str] = {}
        self.context_index: Dict[Tuple[str, str], dict] = {}
        for e in self.vuzor:
            polish_lower = e['polish'].lower()
            key = (polish_lower, e['type and case'])
            self.lookup[key] = e['slovian']
            if 'context' in e and e['context']:
                ctx_key = (polish_lower, e['context'].lower())
                self.context_index[ctx_key] = e

    def translate_decl(self, polish_word: str, case_info: str) -> Optional[str]:
        """Pełna deklinacja: podaj dokładny 'type and case' z JSON"""
        key = (polish_word.lower(), case_info)
        return self.lookup.get(key)

    def get_by_context(self, polish_word: str, context: str) -> Optional[dict]:
        """Znajduje lemma + wszystkie formy po kontekście (rzeczownik/przymiotnik)"""
        ctx_key = (polish_word.lower(), context.lower())
        return self.context_index.get(ctx_key)

    def get_noun_form(self, polish_word: str, case_name: str, number: str = "singular", context: Optional[str] = None) -> Optional[str]:
        """Deklinacja rzeczownika (męski/żeński/nijaki) z kontekstem"""
        if context:
            entry = self.get_by_context(polish_word, context)
            if not entry or 'noun' not in entry['type and case']:
                return None
            base_case = entry['type and case']
        else:
            base_case = None
        full_case = f"noun - jimenьnik: \"{polish_word}\" | {case_name} | {number} - poedinьna ličьba" if number == "singular" else f"noun - jimenьnik: \"{polish_word}\" | {case_name} | munoga ličьba"
        return self.translate_decl(polish_word, full_case) or self.translate_decl(polish_word, base_case) if base_case else None

    def get_adj_form(self, polish_word: str, case_name: str, number: str = "singular", gender: str = "masculine", context: Optional[str] = None) -> Optional[str]:
        """Deklinacja przymiotnika (męski/żeński/nijaki) z kontekstem"""
        if context:
            entry = self.get_by_context(polish_word, context)
            if not entry or 'pridavьnik' not in entry['type and case']:
                return None
        full_case = f"adjective - pridavьnik: \"{polish_word}\" | {case_name} | {number} - poedinьna ličьba | type {gender} - rod'ajь"
        if gender == "masculine":
            full_case += " mǫžьsky"
        elif gender == "feminine":
            full_case += " ženьsky"
        else:
            full_case += " nijaky"
        return self.translate_decl(polish_word, full_case)

decliner = SlovianDecliner()
