import streamlit as st
import json
import re
from deep_translator import GoogleTranslator
from streamlit_javascript import st_javascript

# ================== 1. JĘZYKI I KONFIGURACJA ==================
# Ustawiamy konfigurację na samym początku
st.set_page_config(page_title="Slovo", layout="wide")

@st.cache_resource
def get_all_languages():
    try:
        translator = GoogleTranslator()
        langs = translator.get_supported_languages(as_dict=True)
        return {name.capitalize(): code for name, code in langs.items()}
    except:
        return {"Polish": "pl", "English": "en", "German": "de"}

GOOGLE_LANGS = get_all_languages()
# Łączymy opcje, upewniając się, że klucze są unikalne
ALL_OPTIONS = {"Auto": "auto", "Słowiański": "slo", **GOOGLE_LANGS}

# Słownik tłumaczeń interfejsu
UI_TRANSLATIONS = {
    "pl": {"title": "Tłumacz", "from": "Z języka:", "to": "Na język:", "input": "Wpisz tekst:", "btn": "🔄 Tłumacz", "res": "Wynik:", "warn": "⚠️ Wpisz tekst."},
    "en": {"title": "Translator", "from": "From:", "to": "To:", "input": "Enter text:", "btn": "🔄 Translate", "res": "Result:", "warn": "⚠️ Please enter text."},
    "de": {"title": "Übersetzer", "from": "Von:", "to": "Nach:", "input": "Text eingeben:", "btn": "🔄 Übersetzen", "res": "Ergebnis:", "warn": "⚠️ Text eingeben."},
    "fr": {"title": "Traducteur", "from": "De:", "to": "Vers:", "input": "Entrez le texte:", "btn": "🔄 Traduire", "res": "Résultat:", "warn": "⚠️ Entrez le texte."},
    "es": {"title": "Traductor", "from": "De:", "to": "A:", "input": "Ingrese texto:", "btn": "🔄 Traducir", "res": "Resultado:", "warn": "⚠️ Ingrese texto."}
}

# ================== 2. DYNAMICZNA DETEKCJA JĘZYKA ==================
# Używamy session_state, aby uniknąć resetowania języka przy każdym kliknięciu
if "ui_lang" not in st.session_state:
    # Pobieramy język przeglądarki (np. "pl-PL" lub "en-US")
    js_lang = st_javascript("window.navigator.language")
    
    if js_lang:
        detected = js_lang[:2].lower()
        st.session_state.ui_lang = detected if detected in UI_TRANSLATIONS else "en"
    else:
        # Stan przejściowy, zanim JS zwróci wartość
        st.session_state.ui_lang = "en"

# Przypisujemy aktualne tłumaczenia
ui = UI_TRANSLATIONS.get(st.session_state.ui_lang, UI_TRANSLATIONS["en"])

# ================== 3. LOGIKA I PERSISTENCJA ==================
def get_persisted_target():
    # Pobieranie z localStorage
    code = st_javascript("localStorage.getItem('slovo_target_lang');")
    if code and code in ALL_OPTIONS.values():
        return code
    return 'slo'

def save_target(lang_code):
    st_javascript(f"localStorage.setItem('slovo_target_lang', '{lang_code}');")

# CSS dla lepszego wyglądu
st.markdown("""
    <style>
    .main { max-width: 900px; margin: 0 auto; }
    .stTextArea textarea { font-size: 1.1rem; }
    label { font-weight: 600 !important; }
    </style>
    """, unsafe_allow_html=True)

# ================== 4. FUNKCJE TŁUMACZENIA ==================
@st.cache_data
def load_json_safe(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

osnova = load_json_safe("osnova.json")
vuzor = load_json_safe("vuzor.json")

@st.cache_data
def build_dict(osnova, vuzor):
    pl_to_slo = {}
    slo_to_pl = {}
    for entry in osnova + vuzor:
        pol = entry.get("polish", "").lower().strip()
        slo = entry.get("slovian", "").strip()
        if pol and slo:
            pl_to_slo[pol] = slo
            slo_to_pl[slo.lower()] = pol
    return pl_to_slo, slo_to_pl

pl_to_slo, slo_to_pl = build_dict(osnova, vuzor)

def translate_pl_to_slo(text):
    tokens = re.findall(r'\w+|[^\w\s]|\s+', text)
    result = []
    for t in tokens:
        low = t.lower()
        if low in pl_to_slo:
            res = pl_to_slo[low]
            if t.istitle(): res = res.capitalize()
            elif t.isupper(): res = res.upper()
            result.append(res)
        else:
            result.append(t)
    return "".join(result)

def google_translate(text, src, tgt):
    try:
        return GoogleTranslator(source=src, target=tgt).translate(text)
    except Exception as e:
        return f"(Error: {e})"

# ================== 5. RENDEROWANIE INTERFEJSU ==================
st.write("### 🌐 Slovo")
st.title(ui["title"])

col1, col2 = st.columns(2)

with col1:
    st.selectbox(ui["from"], list(ALL_OPTIONS.keys()), index=0, key="src_lang_name")

with col2:
    persisted = get_persisted_target()
    # Znajdujemy indeks dla zapamiętanego języka
    all_values = list(ALL_OPTIONS.values())
    default_idx = all_values.index(persisted) if persisted in all_values else 1
    
    st.selectbox(ui["to"], list(ALL_OPTIONS.keys()), index=default_idx, key="target_lang_name")

# Zapisywanie wyboru języka docelowego
if "target_lang_name" in st.session_state:
    save_target(ALL_OPTIONS[st.session_state.target_lang_name])

user_input = st.text_area(ui["input"], height=150, placeholder="...")

if st.button(ui["btn"], type="primary"):
    if user_input.strip():
        src_code = ALL_OPTIONS[st.session_state.src_lang_name]
        tgt_code = ALL_OPTIONS[st.session_state.target_lang_name]
        
        with st.spinner('...'):
            if tgt_code == "slo":
                # Do Słowiańskiego: najpierw na polski (jeśli trzeba), potem słownik
                pl_text = google_translate(user_input, src_code, "pl") if src_code != "pl" else user_input
                result = translate_pl_to_slo(pl_text)
            elif src_code == "slo":
                # Ze Słowiańskiego: słownik na polski, potem Google
                tokens = re.findall(r'\w+|[^\w\s]|\s+', user_input)
                pl_text = "".join([slo_to_pl.get(t.lower(), t) for t in tokens])
                result = google_translate(pl_text, "pl", tgt_code)
            else:
                # Standardowe Google Translate
                result = google_translate(user_input, src_code, tgt_code)
            
            st.divider()
            st.markdown(f"### {ui['res']}")
            st.success(result)
    else:
        st.warning(ui["warn"])
