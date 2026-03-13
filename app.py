import streamlit as st

# --- KONFIGURACJA ---
LANGUAGES = {
    "pl": "Polski", "sl": "Prasłowiański", "en": "Angielski",
    "de": "Niemiecki", "fr": "Francuski", "es": "Hiszpański", "ru": "Rosyjski"
}

st.set_page_config(page_title="Tłumacz", layout="wide")

# --- CSS: PRECYZYJNE WYKOŃCZENIE ---
st.markdown("""
<style>
    /* Podciągnięcie całości do góry */
    .stApp { margin-top: -50px; }
    
    .title-text {
        color:#002b49;
        font-weight:800;
        text-align:center;
        font-size:2.2rem;
        margin-bottom: 20px !important;
    }

    /* Wyrównanie pionowe rzędu wyboru języka */
    [data-testid="stHorizontalBlock"] {
        align-items: center !important;
        gap: 0.5rem !important;
    }

    /* Stylizacja list rozwijanych */
    div[data-baseweb="select"] {
        border: 2px solid #2d3748 !important;
        border-radius: 10px !important;
    }

    /* Stylizacja przycisków funkcyjnych (Wklej/Kopiuj) */
    .stButton button {
        background:#002b49 !important;
        color:white !important;
        border-radius:6px !important;
        height: 32px !important;
        font-size: 14px !important;
        padding: 0px 15px !important;
        width: auto !important; /* Przycisk dopasuje się do napisu */
    }

    /* Przycisk zamiany języków (⇄) */
    .swap-btn-container button {
        width: 50px !important;
        height: 40px !important;
        font-size: 20px !important;
        margin-top: 0px !important;
    }

    /* Odstępy między rzędami */
    .row-spacer { margin-top: 15px; }

    /* Pola tekstowe */
    .stTextArea textarea {
        border:2px solid #2d3748 !important;
        border-radius:10px !important;
        padding: 15px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- LOGIKA SESJI ---
if "input_text" not in st.session_state: st.session_state.input_text = ""
if "src_lang" not in st.session_state: st.session_state.src_lang = "pl"
if "tgt_lang" not in st.session_state: st.session_state.tgt_lang = "sl"

def swap_langs():
    st.session_state.src_lang, st.session_state.tgt_lang = \
        st.session_state.tgt_lang, st.session_state.src_lang

# --- LAYOUT ---
st.markdown('<h1 class="title-text">Tłumacz Języka Słowiańskiego (Prasłowiańskiego)</h1>', unsafe_allow_html=True)

# RZĄD 1: Wybór języka
c1, c2, c3 = st.columns([10, 1, 10])
with c1:
    st.selectbox("z", options=list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x], key="src_lang", label_visibility="collapsed")
with c2:
    st.markdown('<div class="swap-btn-container">', unsafe_allow_html=True)
    st.button("⇄", on_click=swap_langs, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
with c3:
    st.selectbox("na", options=list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x], key="tgt_lang", label_visibility="collapsed")

st.markdown('<div class="row-spacer"></div>', unsafe_allow_html=True)

# RZĄD 2: Przyciski Kopiuj/Wklej
b1, _, b2 = st.columns([10, 1, 10])
with b1:
    st.button("📋 Wklej tekst")
with b2:
    st.button("📋 Kopiuj wynik")

# RZĄD 3: Pola tekstowe
t1, _, t2 = st.columns([10, 1, 10])
with t1:
    st.session_state.input_text = st.text_area("in", value=st.session_state.input_text, height=250, label_visibility="collapsed", placeholder="Wpisz tekst...")
with t2:
    # Przykładowe "tłumaczenie" (tu wstaw swoją funkcję)
    wynik = f"({st.session_state.tgt_lang.upper()}) {st.session_state.input_text}" if st.session_state.input_text else ""
    st.text_area("out", value=wynik, height=250, label_visibility="collapsed", key="output_area")

st.markdown("---")
st.caption("Interfejs zoptymalizowany pod kątem estetyki DeepL.")
