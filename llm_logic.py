import json
import os
from collections import defaultdict

def load_data(file):
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def detect_case(tag):
    tag = tag.lower()
    if any(x in tag for x in ["nominative", "jimenovьnik"]): return "nom"
    if any(x in tag for x in ["genitive", "rodilьnik"]): return "gen"
    if any(x in tag for x in ["accusative", "vinьnik"]): return "acc"
    if any(x in tag for x in ["locative", "městьnik"]): return "loc"
    if any(x in tag for x in ["dative", "měrьnik"]): return "dat"
    if any(x in tag for x in ["instrumental", "orǫdьnik"]): return "ins"
    return "nom"

def detect_number(tag):
    return "pl" if any(x in tag for x in ["plural", "munoga ličьba"]) else "sg"

def extract_lemma(tag, slovian):
    if '"' in tag:
        return tag.split('"')[1].strip()
    return slovian.split()[0] if slovian else slovian

def build_models():
    data = load_data("vuzor.json")
    models = defaultdict(lambda: {"endings": {}, "class": "masc"})

    for e in data:
        slov = e.get("slovian", "").strip()
        tag = e.get("type and case", "")
        if not slov: continue
        lemma = extract_lemma(tag, slov)
        case = detect_case(tag)
        num = detect_number(tag)
        key = f"{num}_{case}"
        models[lemma]["lemma"] = lemma
        models[lemma]["endings"][key] = slov
        if lemma.endswith("a"): models[lemma]["class"] = "fem"
        elif lemma[-1] in "oe": models[lemma]["class"] = "neut"

    return list(models.values())

# ========================
# Poprawione reguły dla "z"
# ========================
PREP_CASE = {
    "v":  ("loc", "v"),      # w
    "do": ("gen", "do"),
    "na": ("loc", "na"),
    "o":  ("loc", "o"),
    "k":  ("dat", "k"),
    "su": ("ins", "su"),     # z + narzędnik (z kimś)
    "jiz":("gen", "jiz")     # z + dopełniacz (z kogoś/czegoś)
}

def get_case_from_context(tokens, i):
    word = tokens[i].lower()
    
    # Przyimek bezpośrednio przed
    if i > 0:
        prev = tokens[i-1].lower()
        if prev in ("z", "ze"):
            # Następne słowo decyduje (prosta heurystyka)
            if i+1 < len(tokens) and tokens[i+1].lower() in ("kim", "czym", "nim", "nią", "nimi", "tob", "sob"):
                return "ins"   # z kimś → su + ins
            return "gen"       # z czego/kogo → jiz + gen
        if prev in PREP_CASE:
            return PREP_CASE[prev][0]
    
    # Domyślne reguły zdaniowe
    if i == 0 or any(x in tokens[:i] for x in ["widzi", "idzie", "jest"]):
        return "nom"
    return "acc"

def decline(word, case, number, models):
    best = None
    best_score = float("inf")
    for m in models:
        score = sum(c1 != c2 for c1,c2 in zip(word, m["lemma"])) + abs(len(word)-len(m["lemma"]))
        if score < best_score:
            best_score = score
            best = m
    if not best: return word

    key = f"{number}_{case}"
    return best["endings"].get(key, word)

def process(sentence):
    models = build_models()
    tokens = sentence.lower().split()
    result = []

    for i, word in enumerate(tokens):
        if word in ("z", "ze"):
            # Decyzja su / jiz zostanie podjęta przy następnym rzeczowniku
            continue
        if word in PREP_CASE:
            result.append(PREP_CASE[word][1] if word in PREP_CASE else word)
            continue

        case = get_case_from_context(tokens, i)
        number = "pl" if word.endswith(("y","i","ów","ami","ach")) else "sg"

        result.append(decline(word, case, number, models))

    return " ".join(result)

# Testy
if __name__ == "__main__":
    tests = [
        "Kobieta widzi mężczyznę",
        "Idę z przyjacielem",
        "Zrobiłem to z przyjemnością",
        "Z okna widzę morze",
        "W grodzie",
        "Do grodów",
        "Na komputerach"
    ]
    for t in tests:
        print(t, "→", process(t))
