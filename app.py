import streamlit as st
import json
import os
import re

st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="wide")
st.markdown("""
<style>
.main {background:#0e1117}
.stTextArea textarea {background:#1a1a1a;color:#dcdcdc}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_json(filename):
    return json.load(open(filename, encoding="utf-8")) if os.path.exists(filename) else []

osnova = load_json("osnova.json")

@st.cache_data
def build_dictionaries(data):
    pl_sl = {}
    sl_pl = {}
    for e in data:
        pl = e.get("polish","").strip().lower()
        sl = e.get("slovian","").strip().lower()
        if pl and sl:
            pl_sl[pl] = sl
            sl_pl[sl] = pl
    return pl_sl, sl_pl

pl_to_sl, sl_to_pl = build_dictionaries(osnova)

def translate(text, direction):
    if not text.strip(): return ""
    tokens = re.findall(r'\w+|[^\w\s]', text)
    result = []
    for t in tokens:
        if re.match(r'\w+', t):
            lower = t.lower()
            trans = (pl_to_sl.get(lower, t) if direction == "pl_to_sl" else sl_to_pl.get(lower, t))
            if t.isupper(): trans = trans.upper()
            elif t[0].isupper(): trans = trans.capitalize()
            result.append(trans)
        else:
            result.append(t)
    return re.sub(r'\s+', ' ', ''.join(result)).strip()

st.title("Perkladačь slověnьskogo ęzyka")

col1, col_mid, col2 = st.columns([5, 0.8, 5])

with col1:
    source = st.selectbox("Z:", ["Polski", "Prasłowiański"], key="src_lang")
    text_in = st.text_area("Tekst źródłowy", height=350, placeholder="Wpisz tekst...")

with col_mid:
    if st.button("⇄", use_container_width=True):
        st.session_state.src_lang = "Prasłowiański" if source == "Polski" else "Polski"
        st.rerun()

with col2:
    target = "Prasłowiański" if source == "Polski" else "Polski"
    st.selectbox("Na:", [target], disabled=True)
    if text_in:
        dir_ = "pl_to_sl" if source == "Polski" else "sl_to_pl"
        out = translate(text_in, dir_)
        st.text_area("Tłumaczenie", value=out, height=350, disabled=True)

st.caption("Dla innych języków najpierw przetłumacz na polski (pośrednik zawsze polski), potem tutaj")
