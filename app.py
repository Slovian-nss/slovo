import streamlit as st
import json
import os
import re
from collections import defaultdict

# ================== KONFIGURACJA STRONY ==================

st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="centered")

st.markdown("""
<style>
.main {background:#0e1117}
.stTextArea textarea {background:#1a1a1a;color:#dcdcdc;font-size:1.2rem;border-radius:10px;}
.stSuccess {background-color: #1e2329; border: 1px solid #4caf50; color: #dcdcdc; font-size: 1.3rem;}
.stCaption {color: #888;}
</style>
""", unsafe_allow_html=True)

# ================== ŁADOWANIE I INDEKSOWANIE DANYCH ==================

@st.cache_data
def load_and_build_indices():
    def load_file(filename):
        if not os.path.exists(filename):
            return []
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)

    osnova_data = load_file("osnova.json")
    vuzor_data = load_file("vuzor.json")

    # Indeks form odmienionych (Vuzor) - priorytet
    # Kluczem jest polskie słowo w konkretnej formie (np. "grodzie")
    vuzor_index = {}
    for entry in vuzor_data:
        pl_word = entry.get("polish", "").lower().strip()
        if pl_word:
            # Jeśli jest kilka znaczeń, vuzor zazwyczaj przechowuje konkretne formy
            vuzor_index[pl_word] = entry.get("slovian", "")

    # Indeks form podstawowych (Osnova) - backup
    osnova_index = defaultdict(list)
    for entry in osnova_data:
        pl_word = entry.get("polish", "").lower().strip()
        if pl_word:
            osnova_index[pl_word].append(entry.get("slovian", ""))

    return vuzor_index, osnova_index

vuzor_map, osnova_map = load_and_build_indices()

# ================== LOGIKA TŁUMACZENIA (HARD-CODED ENGINE) ==================

def translate_engine(text, v_map, o_map):
    # Tokenizacja zachowująca interpunkcję i białe znaki
    tokens = re.findall(r'\w+|[^\w\s]|\s+', text)
    result = []

    for token in tokens:
        # Jeśli to spacja lub znak interpunkcyjny, przepisujemy 1:1
        if not re.match(r'\w+', token):
            result.append(token)
            continue

        word_lower = token.lower().strip()
        translated = None

        # 1. SZUKANIE W VUZOR (Formy odmienione - np. "miasta", "grodzie")
        if word_lower in v_map:
            translated = v_map[word_lower]
        
        # 2. SZUKANIE W OSNOVA (Formy podstawowe - np. "miasto", "gród")
        elif word_lower in o_map:
            translated = o_map[word_lower][0]

        # 3. SZUKANIE PO PREFIXIE (Uproszczona stemmatyzacja dla słów min. 4 znaki)
        elif len(word_lower) >= 4:
            prefix = word_lower[:4]
            # Szukamy w vuzorze czegokolwiek co zaczyna się tak samo
            for pl_key, sl_val in v_map.items():
                if pl_key.startswith(prefix):
                    translated = sl_val
                    break
            
            if not translated:
                for pl_key, sl_vals in o_map.items():
                    if pl_key.startswith(prefix):
                        translated = sl_vals[0]
                        break

        # SKŁADANIE WYNIKU
        if translated:
            # Zachowanie wielkości liter
            if token[0].isupper():
                translated = translated.capitalize()
            result.append(translated)
        else:
            # Zgodnie z Twoją zasadą:
            result.append("(ne najdeno slova)")

    return "".join(result)

# ================== INTERFEJS STREAMLIT ==================

st.title("Perkladačь slověnьskogo ęzyka")
st.markdown("#### Lokalny silnik tłumaczenia (bez AI)")

user_input = st.text_area(
    "Vupiši slovo alibo rěčenьje:",
    placeholder="Np. W moim mieście.",
    height=150
)

if user_input:
    # Wykonanie tłumaczenia
    translated_text = translate_engine(user_input, vuzor_map, osnova_map)

    st.markdown("### Vynik perklada:")
    st.success(translated_text)

    # Rozwijana analiza dla użytkownika
    with st.expander("🔍 Detali o slovah (Analiza słownikowa)"):
        clean_words = re.findall(r'\w+', user_input.lower())
        unique_words = list(dict.fromkeys(clean_words)) # zachowaj kolejność, usuń duplikaty
        
        for w in unique_words:
            source = ""
            val = ""
            if w in vuzor_map:
                source = "Vuzor (odmienione)"
                val = vuzor_map[w]
            elif w in osnova_map:
                source = "Osnova (podstawa)"
                val = osnova_map[w][0]
            
            if val:
                st.write(f"**{w}** → `{val}` | Źródło: {source}")
            else:
                st.write(f"**{w}** → ❌ brak w bazie")

# STOPKA
st.divider()
st.caption("Aplikacja korzysta wyłącznie z plików osnova.json oraz vuzor.json. Nie wymaga połączenia z internetem ani kluczy API.")
