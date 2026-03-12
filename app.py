# =========================
# IMPORTY
# =========================

import streamlit as st
import json
import os
import re
from difflib import get_close_matches


# =========================
# ŁADOWANIE DANYCH
# =========================

@st.cache_data
def load_json(path):

    if not os.path.exists(path):
        return []

    with open(path, encoding="utf-8") as f:
        return json.load(f)


osnova = load_json("osnova.json")
vuzor = load_json("vuzor.json")


# =========================
# BUDOWA SŁOWNIKA
# =========================

def build_dictionary():

    pl_ps = {}
    ps_pl = {}

    for e in osnova:

        pl = e.get("polish","").lower()
        ps = e.get("slovian","")

        if pl:
            pl_ps[pl] = ps
            ps_pl[ps] = pl

    return pl_ps, ps_pl


pl_ps, ps_pl = build_dictionary()


# =========================
# TOKENIZER
# =========================

def tokenize(text):

    return re.findall(r'\w+|\S', text)


# =========================
# TŁUMACZENIE PL → PS
# =========================

def translate_pl_ps(text):

    words = tokenize(text)

    result = []

    for w in words:

        key = w.lower()

        if key in pl_ps:

            result.append(pl_ps[key])

        else:

            sim = get_close_matches(key, pl_ps.keys(), 1)

            if sim:
                result.append(pl_ps[sim[0]])
            else:
                result.append("(ne najdeno slova)")

    return " ".join(result)


# =========================
# TŁUMACZENIE PS → PL
# =========================

def translate_ps_pl(text):

    words = tokenize(text)

    result = []

    for w in words:

        if w in ps_pl:
            result.append(ps_pl[w])
        else:
            result.append("(nieznane)")

    return " ".join(result)


# =========================
# INTERFEJS
# =========================

st.set_page_config(layout="wide")

st.title("Perkladačь slověnьskogo ęzyka")

col1, col2 = st.columns(2)

with col1:

    source_lang = st.selectbox(
        "Język źródłowy",
        ["polski","prasłowiański"]
    )

    text = st.text_area(
        "Tekst",
        height=250
    )

with col2:

    target_lang = st.selectbox(
        "Język docelowy",
        ["prasłowiański","polski"]
    )

    if text:

        if source_lang == "polski" and target_lang == "prasłowiański":

            result = translate_pl_ps(text)

        elif source_lang == "prasłowiański" and target_lang == "polski":

            result = translate_ps_pl(text)

        else:

            result = "Nieobsługiwane"

        st.text_area(
            "Tłumaczenie",
            value=result,
            height=250
        )
