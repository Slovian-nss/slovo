import json
import os

class SlovianLogic:
    def __init__(self, osnova_path='osnova.json', vuzor_path='vuzor.json'):
        self.osnova = self._load_json(osnova_path)
        self.vuzor  = self._load_json(vuzor_path)
        self.rules = {
            'ą': 'ǫ', 'ę': 'ę', 'rz': 'rь', 'sz': 'š',
            'cz': 'č', 'ż': 'ž', 'ć': 'cь', 'ś': 'sь'
        }

    def _load_json(self, path):
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def get_suffix(self, vuzor_id, form="m1"):
        return self.vuzor.get(vuzor_id, {}).get(form, "")

    def translate_word(self, word):
        clean = word.lower().strip(".,!?:;()")
        if clean in self.osnova:
            entry = self.osnova[clean]
            if isinstance(entry, dict):
                root = entry.get("osnova", "")
                vid  = entry.get("vuzor", "")
                return root + self.get_suffix(vid)
            return entry
        recon = clean
        for pl, psl in self.rules.items():
            recon = recon.replace(pl, psl)
        if recon and recon[-1] not in "aeiouyǫęьъ":
            recon += "ъ"
        return recon

    def translate_sentence(self, text):
        if not text.strip():
            return ""
        return " ".join(self.translate_word(w) for w in text.split())
