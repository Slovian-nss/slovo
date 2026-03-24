import streamlit as st
import json
import re
from deep_translator import GoogleTranslator

# 1. DYNAMICZNE POBIERANIE WSZYSTKICH JĘZYKÓW GOOGLE
@st.cache_resource
def get_all_languages():
    # Pobiera słownik {nazwa: kod} np. {'polish': 'pl', ...}
    langs = GoogleTranslator().get_supported_languages(as_dict=True)
    # Odwracamy i formatujemy, aby nazwy były z wielkiej litery
    return {name.capitalize(): code for name, code in langs.items()}

GOOGLE_LANGS = get_all_languages()
# Dodanie opcji Auto i Słowiańskiego do listy
ALL_OPTIONS = {"Auto": "auto", "Słowiański (Slo)": "slo", **GOOGLE_LANGS}

# 2. DETEKCJA JĘZYKA I INTERFEJS (I18N)
# Próba pobrania języka z nagłówków (Streamlit 1.30+)
try:
    from streamlit.web.server.browser_utils import get_browser_headers
    headers = get_browser_headers()
    browser_lang = headers.get("Accept-Language", "en").split(",")[0][:2]
except:
    browser_lang = "en"

# Rozszerzona baza tłumaczeń UI
UI_TRANSLATIONS = {
    "pl": {"title": "Tłumacz", "from": "Z języka:", "to": "Na język:", "input": "Wpisz tekst:", "btn": "🔄 Tłumacz", "res": "Wynik:"},
    "en": {"title": "Translator", "from": "From:", "to": "To:", "input": "Enter text:", "btn": "🔄 Translate", "res": "Result:"},
    "de": {"title": "Übersetzer", "from": "Von:", "to": "Nach:", "input": "Text eingeben:", "btn": "🔄 Übersetzen", "res": "Ergebnis:"},
    "fr": {"title": "Traducteur", "from": "De:", "to": "Vers:", "input": "Entrez le texte:", "btn": "🔄 Traduire", "res": "Résultat:"},
    "es": {"title": "Traductor", "from": "De:", "to": "A:", "input": "Ingrese texto:", "btn": "🔄 Traducir", "res": "Resultado:"}
}

# Wybór języka UI (default na angielski, jeśli wykrytego brak w bazie)
lang_code = browser_lang if browser_lang in UI_TRANSLATIONS else "en"
ui = UI_TRANSLATIONS[lang_code]

# ================== KONFIGURACJA STRONY ==================
st.set_page_config(page_title=ui["title"], layout="wide") # 'wide' lepiej dopasowuje się do urządzeń

# CSS dla responsywności i estetyki
st.markdown("""
    <style>
    .main { max-width: 800px; margin: 0 auto; }
    @media (max-width: 600px) {
        .stButton button { width: 100%; }
    }
    </style>
    """, unsafe_allow_html=True)

# ================== LOGIKA SŁOWIAŃSKA ==================
@st.cache_data
def load_dictionaries():
    # Mockup ładowania - w Twoim kodzie zostaw ścieżki do plików json
    # Tu zwracam puste, by kod działał u każdego
    return {}, {}

pl_to_slo, slo_to_pl = load_dictionaries()

def translate_pl_to_slo(text):
    # Twoja oryginalna logika tokenizacji
    tokens = re.findall(r'\w+|[^\w\s]|\s+', text)
    result = [pl_to_slo.get(t.lower(), f"[{t}]") if t.strip() and not t.isspace() else t for t in tokens]
    return "".join(result)

def google_translate(text, src, tgt):
    try:
        return GoogleTranslator(source=src, target=tgt).translate(text)
    except Exception as e:
        return f"Error: {e}"

# ================== INTERFEJS UŻYTKOWNIKA ==================
st.write(f"### 🌐 Slovo")
st.title(ui["title"])

# Dopasowanie kolumn do szerokości ekranu
col1, col2 = st.columns([1, 1])
with col1:
    src_label = st.selectbox(ui["from"], list(ALL_OPTIONS.keys()), index=0)
with col2:
    # Domyślnie ustawiamy na polski (jeśli dostępny) lub drugi na liście
    target_index = list(ALL_OPTIONS.values()).index("pl") if "pl" in ALL_OPTIONS.values() else 1
    tgt_label = st.selectbox(ui["to"], list(ALL_OPTIONS.keys()), index=target_index)

user_input = st.text_area(ui["input"], height=150, placeholder="..." )

if st.button(ui["btn"], type="primary"):
    if user_input:
        src_code = ALL_OPTIONS[src_label]
        tgt_code = ALL_OPTIONS[tgt_label]
        
        with st.spinner('Translating...'):
            if tgt_code == "slo":
                # Tłumaczenie na słowiański (przez pośrednika PL dla lepszej jakości)
                pl_inter = google_translate(user_input, src_code, "pl") if src_code != "pl" else user_input
                result = translate_pl_to_slo(pl_inter)
            elif src_code == "slo":
                # Ze słowiańskiego na dowolny
                pl_inter = " ".join([slo_to_pl.get(w.lower(), w) for w in user_input.split()])
                result = google_translate(pl_inter, "pl", tgt_code)
            else:
                # Standardowe Google -> Google
                result = google_translate(user_input, src_code, tgt_code)
            
            st.divider()
            st.subheader(ui["res"])
            st.success(result)
    else:
        st.warning("⚠️ Please enter text.")
