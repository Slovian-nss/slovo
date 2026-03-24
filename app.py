import streamlit as st
import json
import re
from deep_translator import GoogleTranslator

st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="centered")

# ================== STYLE ==================

st.markdown("""
<style>
.main {background:#0e1117}
.stTextArea textarea {background:#1a1a1a;color:#dcdcdc}
</style>
""", unsafe_allow_html=True)

# ================== LOAD ==================

@st.cache_data
def load_json(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Błąd {filename}: {e}")
        return []

osnova = load_json("osnova.json")
vuzor = load_json("vuzor.json")

# ================== BUILD DICT ==================

@st.cache_data
def build_dict(osnova, vuzor):
    pl_to_slo = {}
    slo_to_pl = {}

    def process(data):
        for entry in data:
            pol = entry.get("polish", "").lower().strip()
            slo = entry.get("slovian", "").strip()

            if pol and slo:
                pl_to_slo[pol] = slo
                slo_to_pl[slo.lower()] = pol

    process(osnova)
    process(vuzor)

    return pl_to_slo, slo_to_pl

pl_to_slo, slo_to_pl = build_dict(osnova, vuzor)

# ================== TRANSLATE ==================

def translate_pl_to_slo(text):
    tokens = re.findall(r'\w+|[^\w\s]|\s+', text)
    result = []

    for token in tokens:
        if re.match(r'\w+', token):
            lower = token.lower()

            # dokładne
            if lower in pl_to_slo:
                translated = pl_to_slo[lower]

            # prefiks
            else:
                translated = None
                for k, v in pl_to_slo.items():
                    if lower.startswith(k[:4]):
                        translated = v
                        break

                if not translated:
                    translated = f"[{token}]"

            if token.istitle():
                translated = translated.capitalize()
            elif token.isupper():
                translated = translated.upper()

            result.append(translated)
        else:
            result.append(token)

    return "".join(result)


def translate_slo_to_pl(text):
    tokens = re.findall(r'\w+|[^\w\s]|\s+', text)
    result = []

    for token in tokens:
        if re.match(r'\w+', token):
            lower = token.lower()
            translated = slo_to_pl.get(lower, token)

            if token.istitle():
                translated = translated.capitalize()
            elif token.isupper():
                translated = translated.upper()

            result.append(translated)
        else:
            result.append(token)

    return "".join(result)

# ================== GOOGLE ==================

def google_translate(text, source, target):
    try:
        return GoogleTranslator(source=source, target=target).translate(text)
    except Exception as e:
        return f"(błąd: {e})"

# ================== UI ==================

st.title("Perkladačь slověnьskogo ęzyka")

langs = {
    "Auto": "auto",
    "Polski": "pl",
    "Angielski": "en",
    "Niemiecki": "de",
    "Francuski": "fr",
    "Hiszpański": "es",
    "Słowiański": "slo"
}

col1, col2 = st.columns(2)

with col1:
    source_lang = st.selectbox("Z języka:", list(langs.keys()))

with col2:
    target_lang = st.selectbox("Na język:", list(langs.keys()), index=6)

user_input = st.text_area("Vupiši tekst:", height=150)

if st.button("🔄 Tłumacz") and user_input:

    src = langs[source_lang]
    tgt = langs[target_lang]

    # ===== NA SŁOWIAŃSKI =====
    if tgt == "slo":
        pl = google_translate(user_input, src, "pl")
        result = translate_pl_to_slo(pl)

    # ===== ZE SŁOWIAŃSKIEGO =====
    elif src == "slo":
        pl = translate_slo_to_pl(user_input)
        result = google_translate(pl, "pl", tgt)

    # ===== NORMAL =====
    else:
        result = google_translate(user_input, src, tgt)

    st.markdown("### Vynik perklada:")
    st.success(result)
