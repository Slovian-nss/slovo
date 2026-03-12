import streamlit as st
import json
import os
import re
from collections import defaultdict
from difflib import get_close_matches

# ===============================
# KONFIGURACJA STRONY
# ===============================

st.set_page_config(
    page_title="Perkladačь slověnьskogo ęzyka",
    layout="wide"
)

st.markdown("""
<style>

.main {
background:#0e1117;
color:white;
}

textarea {
background:#1a1a1a !important;
color:#dcdcdc !important;
font-size:18px !important;
}

</style>
""", unsafe_allow_html=True)

# ===============================
# ŁADOWANIE PLIKÓW
# ===============================

@st.cache_data
def load_json(filename):

    if not os.path.exists(filename):
        return []

    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


osnova = load_json("osnova.json")
vuzor = load_json("vuzor.json")


# ===============================
# MEMORY (SAMOUCZENIE)
# ===============================

def load_memory():

    if os.path.exists("memory.json"):

        with open("memory.json", encoding="utf-8") as f:
            return json.load(f)

    return {}


def learn(source, target):

    if os.path.exists("memory.json"):

        with open("memory.json", encoding="utf-8") as f:
            data = json.load(f)

    else:

        data = {}

    data[source] = target

    with open("memory.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


memory = load_memory()

# ===============================
# BUDOWA SŁOWNIKA
# ===============================

@st.cache_data
def build_dictionary(data):

    dic = defaultdict(list)

    for entry in data:

        key = entry.get("polish", "").lower().strip()

        if key:
            dic[key].append(entry)

    return dic


dictionary = build_dictionary(osnova)

# ===============================
# TOKENIZER
# ===============================

def tokenize(text):

    return re.findall(r'\w+|\S', text)


# ===============================
# TŁUMACZENIE PL → PS
# ===============================

def translate_pl_ps(text):

    words = tokenize(text)

    result = []

    for w in words:

        key = w.lower()

        if key in memory:

            result.append(memory[key])
            continue

        if key in dictionary:

            entry = dictionary[key][0]
            result.append(entry["slovian"])
            continue

        sim = get_close_matches(key, dictionary.keys(), n=1, cutoff=0.8)

        if sim:

            entry = dictionary[sim[0]][0]
            result.append(entry["slovian"])

        else:

            result.append("(ne najdeno slova)")

    return " ".join(result)


# ===============================
# TŁUMACZENIE PS → PL
# ===============================

def translate_ps_pl(text):

    words = tokenize(text)

    result = []

    reverse_dict = {}

    for entry in osnova:
        reverse_dict[entry["slovian"]] = entry["polish"]

    for w in words:

        if w in reverse_dict:

            result.append(reverse_dict[w])

        else:

            result.append("(nieznane)")

    return " ".join(result)


# ===============================
# INTERFEJS
# ===============================

st.title("Perkladačь slověnьskogo ęzyka")

col1, col2 = st.columns(2)

with col1:

    source_lang = st.selectbox(
        "Język źródłowy",
        [
            "polski",
            "prasłowiański"
        ]
    )

    user_input = st.text_area(
        "Tekst",
        height=300,
        placeholder="Np. W miastach jest siła."
    )


with col2:

    target_lang = st.selectbox(
        "Język docelowy",
        [
            "prasłowiański",
            "polski"
        ]
    )

    result = ""

    if user_input:

        if source_lang == "polski" and target_lang == "prasłowiański":

            result = translate_pl_ps(user_input)

        elif source_lang == "prasłowiański" and target_lang == "polski":

            result = translate_ps_pl(user_input)

        else:

            result = "Nieobsługiwane tłumaczenie."

    st.text_area(
        "Tłumaczenie",
        value=result,
        height=300
    )


# ===============================
# POPRAWIANIE TŁUMACZEŃ
# ===============================

st.markdown("---")
st.markdown("### Popraw tłumaczenie (samouczenie)")

correct = st.text_input(
    "Jeśli tłumaczenie jest złe — wpisz poprawne:"
)

if st.button("Zapisz poprawkę"):

    if user_input and correct:

        learn(user_input.lower(), correct)

        st.success("Zapisano w memory.json")

    else:

        st.warning("Wpisz tekst i poprawkę.")
