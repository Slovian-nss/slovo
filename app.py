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

LT_URL = "https://libretranslate.de/translate"

st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="wide")
st.markdown("""<style>.main{background:#0e1117}.stTextArea textarea{background:#1a1a1a;color:#dcdcdc}</style>""", unsafe_allow_html=True)

LANGUAGES = {"Polski": "pl", "Prasłowiański": "sl", "Angielski": "en", "Niemiecki": "de", "Francuski": "fr", "Hiszpański": "es", "Rosyjski": "ru", "Ukraiński": "uk", "Czeski": "cs"}

# --- oryginalne funkcje GitHub / dict / translate / save ---
def get_github_file():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        content = base64.b64decode(data['content']).decode('utf-8')
        return json.loads(content), data['sha']
    return [], None

@st.cache_data
def load_all_data():
    if os.path.exists("osnova.json"):
        with open("osnova.json", "r", encoding="utf-8") as f:
            osnova = json.load(f)
    else:
        osnova = []
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

def translate(text):
    if not text.strip(): return text
    words = [w.lower() for w in re.findall(r'\w+', text)]
    pl_matches = sum(1 for w in words if w in pl_to_sl)
    sl_matches = sum(1 for w in words if w in sl_to_pl)
    to_sl = pl_matches >= sl_matches
    dic = pl_to_sl if to_sl else sl_to_pl
    def repl(m):
        w = m.group(0)
        lw = w.lower()
        if lw in dic and dic[lw]:
            t = dic[lw][0]
            if w.isupper(): return t.upper()
            if w[0].isupper(): return t.capitalize()
            return t
        else:
            return "(ne najdeno slova)" if to_sl else w
    return re.sub(r'\w+', repl, text)

def save_pair_to_github(polish, slovian):
    current_data, sha = get_github_file()
    new_entry = {"polish": polish.strip(), "slovian": slovian.strip()}
    current_data.append(new_entry)
    updated_json = json.dumps(current_data, ensure_ascii=False, indent=2)
    encoded_content = base64.b64encode(updated_json.encode('utf-8')).decode('utf-8')
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    payload = {"message": f"Nauka: {polish} -> {slovian}", "content": encoded_content, "branch": BRANCH, "sha": sha}
    res = requests.put(url, headers=headers, json=payload)
    if res.status_code in [200, 201]:
        st.cache_data.clear()
        st.success("Zapisano w chmurze GitHub!")
        st.rerun()
    else:
        st.error(f"Błąd zapisu: {res.text}")

# --- LibreTranslate + polski pivot ---
def libre_translate(text, src, tgt):
    if src == tgt or not text.strip(): return text
    try:
        r = requests.post(LT_URL, data={"q": text, "source": src, "target": tgt, "format": "text"})
        return r.json().get("translatedText", text) if r.status_code == 200 else text
    except:
        return text

def full_translate(text, source_name, target_name):
    if not text.strip(): return text
    src = LANGUAGES[source_name]
    tgt = LANGUAGES[target_name]
    if src == tgt: return text
    if src == "sl" or tgt == "sl":
        if src == "sl" and tgt == "pl": return translate(text)
        if src == "pl" and tgt == "sl": return translate(text)
        if src == "sl":
            pl_text = translate(text)
            return libre_translate(pl_text, "pl", tgt) if tgt != "pl" else pl_text
        if tgt == "sl":
            pl_text = libre_translate(text, src, "pl") if src != "pl" else text
            return translate(pl_text)
    pl_text = libre_translate(text, src, "pl") if src != "pl" else text
    return libre_translate(pl_text, "pl", tgt) if tgt != "pl" else pl_text

# --- DeepL-like UI ---
st.title("🌍 Perkladačь slověnьskogo ęzyka")

col1, mid, col2 = st.columns([10, 1, 10])

with col1:
    source_name = st.selectbox("Z:", list(LANGUAGES.keys()), index=0, key="source")
    input_text = st.text_area("Tekst źródłowy", height=300, placeholder="Wpisz tekst...")

with mid:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    if st.button("⇄", use_container_width=True):
        st.session_state.source, st.session_state.target = st.session_state.get("target", list(LANGUAGES.keys())[1]), source_name
        st.rerun()

with col2:
    target_name = st.selectbox("Na:", list(LANGUAGES.keys()), index=1, key="target")
    output = full_translate(input_text, source_name, target_name)
    st.text_area("Tłumaczenie", value=output, height=300, disabled=True)

st.divider()
st.subheader("🧠 Naucz tłumacza")
col_a, col_b = st.columns(2)
new_pl = col_a.text_input("Słowo polskie")
new_sl = col_b.text_input("Tłumaczenie słowiańskie")
if st.button("Zapisz do selflearning.json"):
    if new_pl and new_sl:
        with st.spinner("Wysyłanie do GitHub..."):
            save_pair_to_github(new_pl, new_sl)
    else:
        st.warning("Wypełnij oba pola!")
