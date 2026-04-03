def get_case_and_prep(tokens, i):
    if i == 0: 
        return "nom", None
    
    prev = tokens[i-1].lower()
    
    if prev in ("z", "ze"):
        # Decyduje końcówka polskiego słowa (prosta, ale skuteczna heurystyka)
        current = tokens[i].lower()
        if current.endswith(("em", "ą", "im", "ami", "mi", "ą", "ogrodem", "przyjacielem", "nim", "nią", "nimi")):
            return "ins", "su"   # z + narzędnik
        else:
            return "gen", "jiz"  # z + dopełniacz (domyślnie)

    if prev in PREP_RULES:
        return PREP_RULES[prev]
    
    return "acc", None


def decline(word, case, number, models):
    if not word: 
        return "●"
    
    best_model = None
    best_score = float("inf")
    
    for lemma, m in models.items():
        # Lepsze dopasowanie
        score = sum(a != b for a, b in zip(word.lower(), lemma.lower())) + abs(len(word) - len(lemma)) * 2
        if score < best_score:
            best_score = score
            best_model = m
    
    if not best_model:
        return "●"
    
    key = f"{number}_{case}"
    result = best_model["endings"].get(key)
    return result if result else "●"   # zawsze ● gdy brak formy
