import streamlit as st
import json
import os
import re

# Ustawienia strony
st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="wide")

# =========================
# STYL I SKRYPTY JS (Wklejanie)
# =========================
st.markdown("""
<style>
    .stApp { background-color: white; }
    h1, h2, h3, p, label { color: #1a1a1a !important; }
    .stTextArea textarea {
        background-color: #f8f9fa !important;
        color: #1a1a1a !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 8px !important;
    }
    .stButton button { width: 100%; }
</style>
""", unsafe_allow_html=True)

# =========================
# LOGIKA DANYCH
# =========================

def load_all_data():
    def read_json(path):
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        return {}

    osnova = read_json("osnova.json")
    memory = read_json("memory.json")

    pl_to_sl = {}
    sl_to_pl = {}

    if isinstance(osnova, list):
        for item in osnova:
            p = item.get("polish", "").lower().strip()
            s = item.get("slovian", "").lower().strip()
            if p and s:
                pl_to_sl[p] = s
                sl_to_pl[s] = p

    for p, s in memory.items():
        pl_to_sl[p.lower()] = s
        sl_to_pl[s.lower()] = p

    return pl_to_sl, sl_to_pl

def save_memory(source, target, direction):
    memory = {}
    if os.path.exists("memory.json"):
        with open("memory.json", encoding="utf-8") as f:
            try:
                memory = json.load(f)
            except: memory = {}
    
    if direction == "PL -> SL":
        memory[source.lower()] = target
    else:
        memory[target.lower()] = source

    with open("memory.json", "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

# =========================
# FUNKCJE POMOCNICZE
# =========================

def translate_engine(text, dictionary):
    if not text: return ""
    tokens = re.split(r'(\W+)', text)
    result = []
    for token in tokens:
        low_token = token.lower()
        if low_token in dictionary:
            translated = dictionary[low_token]
            if token.isupper(): translated = translated.upper()
            elif token and token[0].isupper(): translated = translated.capitalize()
            result.append(translated)
        else:
            result.append(token)
    return "".join(result)

# =========================
# INTERFEJS
# =========================

pl_to_sl, sl_to_pl = load_all_data()

st.title("Perkladačь slověnьskogo ęzyka")

# Kierunek
direction = st.radio("Kierunek:", ["PL -> SL", "SL -> PL"], horizontal=True)

col1, col2 = st.columns(2)

with col1:
    # Przycisk wklejania (Symulacja, Streamlit wymaga st.button do obsługi stanu)
    if "input_val" not in st.session_state:
        st.session_state.input_val = ""

    # Pokaż "Wklej" tylko gdy pusto
    if st.session_state.input_val == "":
        if st.button("📋 Wklej tekst"):
            # Uwaga: W przeglądarce dostęp do schowka wymaga JS, 
            # tutaj dajemy placeholder, by użytkownik wiedział, że ma wkleić.
            st.info("Użyj Ctrl+V, aby wkleić tekst poniżej.")

    input_text = st.text_area("Tekst źródłowy:", value=st.session_state.input_val, height=200, key="main_input")
    st.session_state.input_val = input_text

with col2:
    # Przycisk kopiowania
    if st.button("📄 Skopiuj tłumaczenie"):
        st.write("Skopiowano do schowka (Ctrl+C)!") # W Streamlit Cloud to tylko informacja

    # Logika tłumaczenia
    if st.button("🚀 Tłumacz"):
        current_dict = pl_to_sl if direction == "PL -> SL" else sl_to_pl
        st.session_state.translation = translate_engine(input_text, current_dict)
    
    if "translation" not in st.session_state:
        st.session_state.translation = ""
        
    st.text_area("Wynik:", value=st.session_state.translation, height=200, key="main_output")

# =========================
# PANEL MODERATORA
# =========================
st.markdown("---")
st.subheader("Popraw tłumaczenie (Admin)")

# Logika czyszczenia pól po wysłaniu
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

with st.container():
    col_pwd, col_btn_pwd = st.columns([3, 1])
    with col_pwd:
        pwd = st.text_input("Hasło", type="password")
    with col_btn_pwd:
        st.write(" ") # Odstęp
        check_pwd = st.button("Zaloguj")

    if pwd == "Rozeta*8" or check_pwd:
        if pwd == "Rozeta*8":
            c1, c2 = st.columns(2)
            with c1:
                src_word = st.text_input("Słowo źródłowe", key="src_in")
            with c2:
                trg_word = st.text_input("Poprawne tłumaczenie", key="trg_in")
            
            if st.button("Zaktualizuj bazę"):
                if src_word and trg_word:
                    save_memory(src_word, trg_word, direction)
                    st.success(f"✅ Dodano: {src_word} -> {trg_word}")
                    # Czyszczenie przez rerun
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("❌ Błąd: Oba pola muszą być wypełnione!")
        else:
            if pwd != "":
                st.error("❌ Błędne hasło")
