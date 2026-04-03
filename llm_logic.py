import json
import os
import re

def load_json(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_json(data, filename):
    if filename == 'osnova.json':
        data = sorted(data, key=lambda x: x.get('polish', '').lower())
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_vuzor_tags(tag_string):
    """
    Analizuje Twoje tagi: 'noun - jimenьnik: "obětьnica" | genitive | plural | type feminine'
    """
    tag_string = tag_string.lower()
    info = {
        "case": "nom",
        "num": "sg",
        "gender": "masc"
    }
    
    # Mapowanie przypadków
    cases = {"nominative": "nom", "accusative": "acc", "genitive": "gen", 
             "locative": "loc", "dative": "dat", "instrumental": "ins"}
    for k, v in cases.items():
        if k in tag_string: info["case"] = v
            
    if "plural" in tag_string: info["num"] = "pl"
    if "feminine" in tag_string: info["gender"] = "fem"
    elif "neuter" in tag_string: info["gender"] = "neut"
    
    return info

def get_ending(slovian_word):
    """Wyciąga końcówkę (ostatnie 1-2 znaki)"""
    vowels = "aoyěęǫъьiue"
    if len(slovian_word) > 1 and slovian_word[-1] in vowels:
        if len(slovian_word) > 2 and slovian_word[-2] in vowels:
            return slovian_word[-2:]
        return slovian_word[-1]
    return ""

def learn_grammar_from_vuzor():
    """
    Kluczowa funkcja: analizuje vuzor.json i tworzy mapę końcówek.
    """
    vuzor_data = load_json('vuzor.json')
    grammar_map = {} # { "noun_masc": { "pl_gen": "ovъ" } }

    for entry in vuzor_data:
        tags = parse_vuzor_tags(entry.get('type and case', ''))
        s_word = entry.get('slovian', '')
        
        if not s_word: continue
        
        # Określamy typ (uproszczony)
        w_type = f"noun_{tags['gender']}"
        if w_type not in grammar_map: grammar_map[w_type] = {}
        
        # Zapisujemy końcówkę dla danego przypadku i liczby
        key = f"{tags['num']}_{tags['case']}"
        grammar_map[w_type][key] = get_ending(s_word)
        
    return grammar_map

def learn_from_examples():
    """Uczy się rdzeni z example_sentences.json"""
    examples = load_json('example_sentences.json')
    osnova = load_json('osnova.json')
    existing_polish = {item.get('polish', '').lower(): item for item in osnova}

    for ex in examples:
        p_word = ex.get('polish', '').lower().strip()
        s_word = ex.get('slovian', '').strip()
        
        if p_word and s_word and p_word not in existing_polish:
            # Automatyczne wyznaczanie rdzenia (stem)
            stem = s_word
            for end in ['ъ', 'a', 'o', 'e', 'ь']:
                if s_word.endswith(end):
                    stem = s_word[:-len(end)]
                    break
            
            osnova.append({
                "polish": p_word,
                "slovian": s_word,
                "stem": stem,
                "type": "noun_masc" if s_word.endswith('ъ') else "noun_fem" if s_word.endswith('a') else "noun_neut",
                "context": ex.get("context", "")
            })
    
    save_json(osnova, 'osnova.json')

def translate_with_grammar(polish_word, target_case='gen', target_num='pl'):
    """
    Główna funkcja translatora: łączy rdzeń z końcówką z vuzora.
    """
    osnova = load_json('osnova.json')
    grammar = learn_grammar_from_vuzor()
    
    match = next((i for i in osnova if i['polish'].lower() == polish_word.lower()), None)
    
    if match and 'stem' in match:
        w_type = match.get('type', 'noun_masc')
        key = f"{target_num}_{target_case}"
        
        # Jeśli mamy końcówkę w vuzorze, doklejamy ją
        if w_type in grammar and key in grammar[w_type]:
            return match['stem'] + grammar[w_type][key]
        
    return polish_word # Fallback

if __name__ == "__main__":
    learn_from_examples()
    # Przykład użycia: print(translate_with_grammar("dom", "gen", "pl")) -> "domovъ"
