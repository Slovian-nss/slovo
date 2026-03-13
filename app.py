import streamlit as st
import json
import os
import re
import requests
import base64
from collections import defaultdict

# --- KONFIGURACJA ---
GITHUB_TOKEN = "MYTOKEN"
REPO_OWNER = "Slovian-nss"
REPO_NAME = "slovian-translator"
FILE_PATH = "selflearning.json"
BRANCH = "main"

LANGUAGES = {
    "pl": "Polski",
    "sl": "Prasłowiański",
    "en": "Angielski",
    "de": "Niemiecki",
    "fr": "Francuski",
    "es": "Hiszpański",
    "ru": "Rosyjski"
}

st.set_page_config(page_title="DeepL Slověnьsk", layout="wide")

# --- STYLIZACJA (DeepL UI) ---
st.markdown("""
<style>
    .stApp { background-color: #f0f2f5; color: #1a1a1b; }
    
    /* Ciemne obramowania pól tekstowych i selectboxów */
    .stTextArea textarea, .stSelectbox div[data-baseweb="select"] { 
        border: 2px solid #2d3748 !important; 
        border-radius: 10px !important; 
        background-color: white !important;
        color: #1a1a1b !important;
    }

    /* Stylizacja przycisku zamiany języków */
    .swap-btn-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
        padding-top: 25px; /* Wyśrodkowanie względem selectboxów */
    }
    
    .stButton button {
        background-color: #002b49; 
        color: white; 
        border-radius: 8px; 
        border: none; 
        width: 45px;
        height: 40px;
        transition: 0.3s;
    }
    .stButton button:hover { background-color: #004a7c; color: white; transform: scale(1.05); }
    
    h1 { color: #002b49; font-weight: 800; text-align: center; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- LOGIKA TŁUMACZENIA (Skrócona dla czytelności) ---
@st.cache_data
def load_all_data():
    osnova = []
    if os.path.exists("osnova.json"):
        with open("osnova.json", "r", encoding="utf-8") as f:
            osnova = json.load(f)
    # Tutaj pobieranie z github...
    return osnova

all_data = load_all_data()

@st.cache_data
def build_dictionaries(data):
    pl_sl = defaultdict(list)
    sl_pl = defaultdict(list)
    for e in data:
        pl, sl = e.get("polish","").lower().strip(), e.get("slovian","").lower().strip()
        if pl: pl_sl[pl].append(e.get("slovian",""))
        if sl: sl_pl[sl].append(e.get("polish",""))
    return pl_sl, sl_pl

pl_to_sl, sl_to_pl = build_dictionaries(all_data)

def master_translate(text, src, tgt):
    # Logika pivot (uproszczona dla demo)
    if not text.strip(): return ""
    return f"Tłumaczenie z {src} na {tgt}: {text}" # Tu wstaw pełną logikę z poprzedniego kroku

# --- UI APLIKACJI ---
st.title("DeepL Slověnьsk")

# Wiersz z wyborem języków i przyciskiem SWAP
c_lang_1, c_swap, c_lang_2 = st.columns([10, 1, 10])

with c_lang_1:
    src_lang = st.selectbox("Język źródłowy", options=list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x], index=0, label_visibility="collapsed")

with c_swap:
    st.markdown('<div class="swap-btn-container">', unsafe_allow_html=True)
    if st.button("⇄"):
        st.rerun() # W pełnej wersji tutaj zamieniamy wartości w st.session_state
    st.markdown('</div>', unsafe_allow_html=True)

with c_lang_2:
    tgt_lang = st.selectbox("Język docelowy", options=list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x], index=1, label_visibility="collapsed")

# Wiersz z polami tekstowymi
c_text_1, c_spacer, c_text_2 = st.columns([10, 1, 10])

with c_text_1:
    source_text = st.text_area("Wpisz tekst", placeholder="Wpisz tekst do przetłumaczenia...", height=350, key="src_text", label_visibility="collapsed")

with c_text_2:
    translated_result = ""
    if source_text:
        with st.spinner('Tłumaczenie...'):
            translated_result = master_translate(source_text, src_lang, tgt_lang)
    
    st.text_area("Wynik", value=translated_result, height=350, key="tgt_text", disabled=False, label_visibility="collapsed")

st.markdown("---")
st.caption("Prasłowiański Translator v2.0 | Język pomostowy: Polski")
