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

# ================== INDEKSOWANIE DANYCH ==================
@st.cache_data
def load_data():
    def load_json(name):
        if not os.path.exists(name): return []
        with open(name, "r", encoding="utf-8") as f: return json.load(f)
    
    db = defaultdict(list)
    # Łączymy vuzor i osnova
    for entry in load_json("vuzor.json") + load_json("osnova.json"):
        pl = entry.get("polish", "").lower().strip()
        if pl: db[pl].append(entry)
    return db

DB = load_data()

# ================== SILNIK TŁUMACZĄCY V4 ==================

# Przyimki i przypadek, który wymuszają
RULES = {
    "w": "locative", "we": "locative", "o": "locative", "na": "locative",
    "do": "genitive", "z": "genitive", "dla": "genitive", "bez": "genitive",
    "ku": "dative", "przeciw": "dative"
}

def find_correct_form(pl_word, required_case=None):
    options = DB.get(pl_word, [])
    
    if not options and len(pl_word) >= 4:
        # Próba znalezienia po rdzeniu, jeśli brak dokładnego słowa
        stem = pl_word[:4]
        for key, entries in DB.items():
            if key.startswith(stem):
                options.extend(entries)

    if options:
        # Jeśli szukamy po przyimku, MUSI to być rzeczownik (noun) w odpowiednim przypadku
        if required_case:
            for opt in options:
                info = opt.get("type and case", "").lower()
                # Kluczowa poprawka: musi zawierać 'noun' ORAZ wymagany przypadek
                if "noun" in info and required_case in info:
                    return opt.get("slovian")
            
            # Jeśli nie znaleźliśmy idealnego rzeczownika, szukamy jakiegokolwiek rzeczownika
            for opt in options:
                if "noun" in opt.get("type and case", "").lower():
                    return opt.get("slovian")

        # Jeśli brak kontekstu przyimkowego, bierzemy pierwszy rekord
        return options[0].get("slovian")

    return None

def translate_v4(text):
    tokens = re.findall(r'\w+|[^\w\s]|\s+', text)
    output = []
    next_case = None

    for token in tokens:
        if not re.match(r'\w+', token):
            output.append(token)
            continue

        low = token.lower().strip()
        
        # Pobieramy tłumaczenie uwzględniając wymóg części mowy
        translated = find_correct_form(low, next_case)
        
        # Ustawiamy kontekst dla następnego słowa
        next_case = RULES.get(low)

        if translated:
            if token[0].isupper(): translated = translated.capitalize()
            output.append(translated)
        else:
            output.append("(ne najdeno slova)")

    return "".join(output)

# ================== INTERFEJS ==================
st.title("Perkladačь slověnьskogo ęzyka")
st.subheader("Silnik V4: Rozpoznawanie części mowy")

user_input = st.text_area("Vupiši rěčenьje:", placeholder="Np. W moim ogrodzie.", height=150)

if user_input:
    res = translate_v4(user_input)
    st.markdown("### Vynik perklada:")
    st.success(res)
    
    with st.expander("Dlaczego tak odmieniło?"):
        st.write("Silnik V4 wymusza wybór rzeczownika (`noun`) po przyimkach, co zapobiega myleniu 'ogrodu' z 'ogradzać'.")
