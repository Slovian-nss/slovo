import streamlit as st
from logic import SlovianLogic

if "translator" not in st.session_state:
    st.session_state.translator = SlovianLogic()

st.set_page_config(page_title="Słowiański Tłumacz", layout="centered")

st.markdown("""
<style>
    .stApp { background: #0d1117; color: #c9d1d9; }
    .stTextArea textarea { background: #0d1117; color: #e6edf3; border: 1px solid #30363d; border-radius: 6px; }
    .stButton > button { background: #238636; color: white; border: none; border-radius: 6px; width: 100%; font-weight: bold; }
    .stButton > button:hover { background: #2ea043; }
    .output { margin-top: 1.5rem; padding: 1.2rem; background: #010409; border-radius: 6px; border-left: 4px solid #58a6ff; color: #ffa657; font-size: 1.3em; }
</style>
""", unsafe_allow_html=True)

st.title("Slovian Translator (NSS)")

txt = st.text_area("", placeholder="Wpisz polskie zdanie...", height=120, label_visibility="collapsed")

if st.button("REKONSTRUUJ"):
    if txt.strip():
        result = st.session_state.translator.translate_sentence(txt)
        st.markdown(f'<div class="output"><strong>Rezultat:</strong><br>{result}</div>', unsafe_allow_html=True)
