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

# --- STYLIZACJA (Poprawione obramowania) ---
st.markdown("""
<style>
    /* Tło aplikacji */
    .stApp { background-color: #f0f2f5; color: #1a1a1b; }
    
    /* Główne kontenery tekstowe i selectboxy */
    .stTextArea textarea, .stSelectbox div[data-baseweb="select"] { 
        border: 2px solid #4a5568 !important; /* Ciemniejszy stalowy kolor obramowania */
        border-radius: 10px !important; 
        background-color: white !important;
        color: #1a1a1b !important;
    }

    /* Poprawka dla samych pól wyboru (select) */
    div[data-baseweb="select"] {
        border: 2px solid #2d3748 !important;
    }

    .stButton button {
        background-color: #002b49; color: white; border-radius: 8px; border: none; font-weight: bold;
    }
    .stButton button:hover { background-color: #004a7c; color: white; border: none; }
    
    h1 { color: #002b49; font-weight: 800; text-align: center; margin-bottom: 30px; }
    
    /* Ukrycie dekoracji Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- LOGIKA DANYCH (Bez zmian) ---
def get_github_file():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            content = base64.b64decode(data['content']).decode('utf-8')
            return json.loads(content), data['sha']
    except:
        pass
    return [], None

@st.cache_data
def load_all_data():
    osnova = []
    if os.path.exists("osnova.json"):
        with open("osnova.json", "r", encoding="utf-8") as f:
            osnova = json.load(f)
    selflearning, _ = get_github_file()
    return osnova + selflearning

all_data = load_all_data()

@st.cache_data
def build_dictionaries(data):
    pl_sl = defaultdict(list)
    sl_pl = defaultdict(list)
    for e in data:
        pl = e.get("polish","").lower().strip()
        sl = e.get("slovian","").lower().strip()
        if pl: pl_sl[pl].append(e.get("slovian",""))
        if sl: sl_pl[sl].append(e.get("polish",""))
    return pl_sl, sl_pl

pl_to_sl, sl_to_pl = build_dictionaries(all_data)

# --- TŁUMACZENIE (Pivot Logic) ---
def external_translate(text, source_lang, target_lang):
    if source_lang == target_lang: return text
    url = f"https://api.mymemory.translated.net/get?q={text}&langpair={source_lang}|{target_lang}"
    try:
        res = requests.get(url).json()
        return res['responseData']['translatedText']
    except:
        return text

def local_translate(text, to_sl=True):
    dic = pl_to_sl if to_sl else sl_to_pl
    def repl(m):
        w = m.group(0); lw = w.lower()
        if lw in dic and dic[lw]:
            t = dic[lw][0]
            if w.isupper(): return t.upper()
            if w[0].isupper(): return t.capitalize()
            return t
        return f"[{w}]" if to_sl else w
    return re.sub(r'\w+', repl, text)

def master_translate(text, src, tgt):
    if not text.strip(): return ""
    if tgt == "sl":
        if src != "pl":
            text = external_translate(text, src, "pl")
        return local_translate(text, to_sl=True)
    elif src == "sl":
        polish_text = local_translate(text, to_sl=False)
        if tgt == "pl": return polish_text
        return external_translate(polish_text, "pl", tgt)
    else:
        return external_translate(text, src, tgt)

# --- UI APLIKACJI ---
st.title("DeepL Slověnьsk")

# Główny panel tłumacza
with st.container():
    c1, mid, c2 = st.columns([10, 1, 10])
    
    with c1:
        src_lang = st.selectbox("Język źródłowy", options=list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x], index=0)
        source_text = st.text_area("Tekst do przetłumaczenia", placeholder="Wpisz tekst...", height=300, key="src")
        
    with mid:
        st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
        st.button("⇄", help="Zamień języki (funkcja wizualna)")

    with c2:
        tgt_lang = st.selectbox("Język docelowy", options=list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x], index=1)
        
        translated_result = ""
        if source_text:
            with st.spinner('Tłumaczenie...'):
                translated_result = master_translate(source_text, src_lang, tgt_lang)
        
        st.text_area("Wynik tłumaczenia", value=translated_result, height=300, key="tgt", disabled=False)

st.markdown("---")
st.caption("Tłumacz wykorzystuje język polski jako pomost dla języków nowożytnych.")
