import streamlit as st
import json
import os
import re
import requests
import base64
from collections import defaultdict

# --- KONFIGURACJA GITHUB ---
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

st.set_page_config(page_title="Tłumacz Słowiańskiego Języka", layout="wide")

# --- STYLIZACJA (DeepL Pro Style) ---
st.markdown("""
<style>
    .stApp { background-color: #f0f2f5; color: #1a1a1b; }
    
    /* Wyraźne, ciemne obramowania pól */
    .stTextArea textarea, div[data-baseweb="select"] { 
        border: 2px solid #2d3748 !important; 
        border-radius: 10px !important; 
        background-color: white !important;
        color: #1a1a1b !important;
    }

    /* Wycentrowanie przycisku SWAP */
    .swap-container {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        margin-top: 0px;
    }
    
    /* Przyciski główne */
    .stButton button {
        background-color: #002b49; 
        color: white !important; 
        border-radius: 8px; 
        border: none; 
        font-weight: bold;
        transition: 0.2s;
    }
    .stButton button:hover { background-color: #004a7c; transform: translateY(-1px); }

    /* Przyciski kopiowania - mniejsze */
    .copy-btn-row {
        margin-bottom: -35px;
        position: relative;
        z-index: 10;
        display: flex;
        justify-content: flex-start;
    }

    h1 { color: #002b49; font-weight: 800; text-align: center; margin-bottom: 30px; }
</style>
""", unsafe_allow_html=True)

# --- LOGIKA TŁUMACZENIA (Skrócona dla czytelności posta) ---
@st.cache_data(ttl=60)
def load_data():
    osnova = []
    if os.path.exists("osnova.json"):
        with open("osnova.json", "r", encoding="utf-8") as f:
            osnova = json.load(f)
    return osnova

all_data = load_data()

def translate_engine(text, src, tgt):
    if not text.strip(): return ""
    # Tutaj Twoja działająca już logika (external_api + local_slovian_logic)
    # Zostawiam placeholder, wklej tu kod z poprzedniej odpowiedzi
    return f"Przetłumaczono: {text}" # Tu wstaw pełną logikę translate_engine

# --- SESSION STATE ---
if 'input_text' not in st.session_state: st.session_state.input_text = ""
if 'src_lang' not in st.session_state: st.session_state.src_lang = "pl"
if 'tgt_lang' not in st.session_state: st.session_state.tgt_lang = "sl"

def swap_action():
    old_src = st.session_state.src_lang
    st.session_state.src_lang = st.session_state.tgt_lang
    st.session_state.tgt_lang = old_src

# --- UI ---
st.title("Tłumacz Słowiańskiego Języka")

# Wiersz wyboru języków
c_lang_1, c_swap, c_lang_2 = st.columns([10, 1, 10])

with c_lang_1:
    st.selectbox("Źródło", options=list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x], key="src_lang", label_visibility="collapsed")

with c_swap:
    st.markdown('<div class="swap-container">', unsafe_allow_html=True)
    st.button("⇄", on_click=swap_action, key="swap_btn")
    st.markdown('</div>', unsafe_allow_html=True)

with c_lang_2:
    st.selectbox("Cel", options=list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x], key="tgt_lang", label_visibility="collapsed")

# Wiersz z polami tekstowymi
t_col1, t_spacer, t_col2 = st.columns([10, 1, 10])

with t_col1:
    st.button("📋 Kopiuj", key="copy_src", help="Kopiuj tekst źródłowy")
    input_val = st.text_area("Input", key="input_text_area", value=st.session_state.input_text, height=350, label_visibility="collapsed")
    st.session_state.input_text = input_val
    if st.button("Tłumacz ➔", use_container_width=True):
        st.rerun()

with t_col2:
    st.button("📋 Kopiuj wynik", key="copy_tgt", help="Kopiuj przetłumaczony tekst")
    # Generowanie tłumaczenia
    output_val = translate_engine(st.session_state.input_text, st.session_state.src_lang, st.session_state.tgt_lang)
    st.text_area("Output", value=output_val, height=350, label_visibility="collapsed")

st.markdown("---")
