import streamlit as st
import json
import os
import re

st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="wide", page_icon="🌾")

st.markdown("""
<style>
    .main {background:#0f1117;}
    .stTextArea textarea {background:#1a1f2e;color:#e6e6e6;font-size:1.1rem;border-radius:12px;border:1px solid #2d3748;}
    .translate-btn {background:linear-gradient(90deg,#0066ff,#0052cc);color:white;font-size:1.25rem;font-weight:700;padding:14px 40px;border-radius:50px;border:none;width:100%;margin:10px 0;}
    .translate-btn:hover {background:linear-gradient(90deg,#3388ff,#0066ff);box-shadow:0 6px 20px rgba(0,102,255,0.5);}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    if not os.path.exists("osnova.json"): return {}, {}
    with open("osnova.json", encoding="utf-8") as f:
        data = json.load(f)
    pl_sl = {e["polish"].strip().lower(): e["slovian"].strip() for e in data if e.get("polish") and e.get("slovian")}
    return pl_sl, {v.lower(): k for k, v in pl_sl.items()}

pl_to_sl, sl_to_pl = load_data()

def translate(text, direction):
    if not text.strip(): return ""
    tokens = re.findall(r'\w+|[^\w\s]', text)
    dic = pl_to_sl if direction == "pl→sl" else sl_to_pl
    result = []
    for t in tokens:
        if t.isalpha():
            lower = t.lower()
            trans = dic.get(lower, lower)
            if t.isupper(): trans = trans.upper()
            elif t[0].isupper(): trans = trans.capitalize()
            result.append(trans)
        else:
            result.append(t)
    return re.sub(r'\s+', ' ', ''.join(result)).strip()

if "output" not in st.session_state: st.session_state.output = ""

st.title("Perkladačь slověnьskogo ęzyka")

col1, col_swap, col2 = st.columns([5, 1, 5])

with col1:
    src_lang = st.selectbox("Z:", ["Polski", "Prasłowiański"], key="src")
    text_in = st.text_area("Tekst źródłowy", height=380, placeholder="Wpisz tekst...", key="input_text")

with col_swap:
    st.write("")
    if st.button("⇄", key="swap"):
        curr_in = st.session_state.get("input_text", "")
        curr_out = st.session_state.get("output", "")
        st.session_state.input_text = curr_out
        st.session_state.output = curr_in
        st.session_state.src = "Prasłowiański" if src_lang == "Polski" else "Polski"
        st.rerun()

with col2:
    tgt_lang = "Prasłowiański" if src_lang == "Polski" else "Polski"
    st.selectbox("Na:", [tgt_lang], disabled=True)
    st.text_area("Tłumaczenie", value=st.session_state.output, height=380, disabled=True)

if st.button("Przełóż", type="primary", use_container_width=True):
    if text_in.strip():
        direction = "pl→sl" if src_lang == "Polski" else "sl→pl"
        st.session_state.output = translate(text_in, direction)
        st.rerun()

st.caption("Dla innych języków najpierw przetłumacz na polski (pośrednik zawsze polski), potem tutaj")
