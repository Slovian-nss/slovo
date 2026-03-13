import streamlit as st

# --- KONFIGURACJA ---
LANGUAGES = {
    "pl": "Polski",
    "sl": "Prasłowiański",
    "en": "Angielski",
    "de": "Niemiecki",
    "fr": "Francuski",
    "es": "Hiszpański",
    "ru": "Rosyjski"
}

st.set_page_config(page_title="Tłumacz Języka Słowiańskiego", layout="wide")

# --- CSS ---
st.markdown("""
<style>
    .stApp { background:#f0f2f5; }
    .title-text {
        color:#002b49;
        font-weight:800;
        text-align:center;
        font-size:2.2rem;
        margin-top:-20px;
        margin-bottom:25px;
    }
    /* Stylizacja selectboxów i textarea */
    div[data-baseweb="select"], .stTextArea textarea {
        border:2px solid #2d3748 !important;
        border-radius:10px !important;
        background:white !important;
    }
    .stButton button {
        background:#002b49;
        color:white !important;
        border-radius:8px;
        font-weight:bold;
    }
</style>
""", unsafe_allow_html=True)

# --- SILNIK TŁUMACZENIA ---
def translate_engine(text, src, tgt):
    if not text.strip():
        return ""
    # Logika przykładowa (tu wepnij API)
    return f"[Tłumaczenie z {src} na {tgt}]: {text}"

# --- SESSION STATE ---
if "src_lang" not in st.session_state:
    st.session_state.src_lang = "pl"
if "tgt_lang" not in st.session_state:
    st.session_state.tgt_lang = "sl"
if "input_text" not in st.session_state:
    st.session_state.input_text = ""

def swap_languages():
    st.session_state.src_lang, st.session_state.tgt_lang = \
        st.session_state.tgt_lang, st.session_state.src_lang

# --- UI ---
st.markdown('<h1 class="title-text">Tłumacz Języka Słowiańskiego</h1>', unsafe_allow_html=True)

# Wybór języków
col_l, col_s, col_r = st.columns([10, 1.2, 10])

with col_l:
    st.selectbox("Z:", options=list(LANGUAGES.keys()), 
                 format_func=lambda x: LANGUAGES[x], 
                 key="src_lang", label_visibility="collapsed")

with col_s:
    st.write(" ") # Odstęp pionowy
    st.button("⇄", on_click=swap_languages, use_container_width=True)

with col_r:
    st.selectbox("Na:", options=list(LANGUAGES.keys()), 
                 format_func=lambda x: LANGUAGES[x], 
                 key="tgt_lang", label_visibility="collapsed")

# Pola tekstowe
t_l, _, t_r = st.columns([10, 1.2, 10])

with t_l:
    # Używamy on_change by tekst zapisywał się w sesji
    input_txt = st.text_area(
        "Tekst źródłowy",
        value=st.session_state.input_text,
        height=300,
        placeholder="Wpisz tekst do przetłumaczenia...",
        label_visibility="collapsed",
        key="main_input"
    )
    st.session_state.input_text = input_txt

with t_r:
    wynik = translate_engine(
        st.session_state.input_text,
        st.session_state.src_lang,
        st.session_state.tgt_lang
    )
    st.text_area(
        "Wynik",
        value=wynik,
        height=300,
        label_visibility="collapsed",
        disabled=False # Ustaw True, jeśli użytkownik ma tylko czytać
    )

st.markdown("---")
st.caption("Interfejs zoptymalizowany pod kątem estetyki DeepL.")
