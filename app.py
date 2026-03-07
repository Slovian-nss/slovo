import streamlit as st
import json
import os
import re
from collections import defaultdict

# ================== KONFIGURACJA ==================
st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="centered")

st.markdown("""
<style>
.main {background:#0e1117}
.stTextArea textarea {background:#1a1a1a;color:#dcdcdc;font-size:1.2rem;}
.stSuccess {background-color: #1e2329; border: 1px solid #4caf50; font-size: 1.3rem;}
</style>
""", unsafe_allow_html=True)

# ================== BAZA WIEDZY ==================
@st.cache_data
def load_and_build_indices():
    def load_file(filename):
        if not os.path.exists(filename): return []
        with open(filename, "r", encoding="utf-8") as f: return json.load(f)

    osnova = load_file("osnova.json")
    vuzor = load_file("vuzor.json")

    # Mapowanie: polskie_slowo -> lista rekordów z gramatyką
    # Pozwala nam to wybrać odpowiedni przypadek
    full_index = defaultdict(list)
    for entry in vuzor + osnova:
        pl = entry.get("polish", "").lower().strip()
        if pl:
            full_index[pl].append(entry)
    
    return full_index

db = load_and_build_indices()

# ================== LOGIKA GRAMATYCZNA ==================
# Prosta mapa: polski przyimek -> wymagany przypadek w slovian
PREPOSITION_RULES = {
    "w": "locative",
    "we": "locative",
    "o": "locative",
    "ku": "dative",
    "do": "genitive",
    "z": "genitive",
    "na": "locative"
}

def find_best_match(pl_word, required_case=None):
    matches = db.get(pl_word, [])
    if not matches:
        return None
    
    # 1. Próbujemy dopasować przypadek (jeśli kontekst go narzucił)
    if required_case:
        for m in matches:
            gramatyka = m.get("type and case", "").lower()
            if required_case in gramatyka:
                return m.get("slovian")

    # 2. Jeśli nie ma przypadku lub nie znaleźliśmy, bierzemy pierwszy dostępny rekord
    return matches[0].get("slovian")

def translate_engine(text):
    tokens = re.findall(r'\w+|[^\w\s]|\s+', text)
    result = []
    next_required_case = None

    for i, token in enumerate(tokens):
        if not re.match(r'\w+', token):
            result.append(token)
            continue

        word_lower = token.lower().strip()
        
        # Sprawdzamy czy obecne słowo jest przyimkiem narzucającym przypadek następnemu
        current_case = next_required_case
        next_required_case = PREPOSITION_RULES.get(word_lower)

        # Szukanie tłumaczenia
        translated = find_best_match(word_lower, current_case)

        if translated:
            if token[0].isupper():
                translated = translated.capitalize()
            result.append(translated)
        else:
            result.append("(ne najdeno slova)")

    return "".join(result)

# ================== UI ==================
st.title("Perkladačь slověnьskogo ęzyka")
user_input = st.text_area("Vupiši rěčenьje:", placeholder="Np. W moim ogrodzie.", height=150)

if user_input:
    res = translate_engine(user_input)
    st.markdown("### Vynik perklada:")
    st.success(res)

    with st.expander("Analiza kontekstowa"):
        st.write("Silnik próbuje dopasować przypadki (locative, genitive) na podstawie przyimków.")
