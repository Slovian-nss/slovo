import streamlit as st
import json
import os
import re
import argostranslate.package
import argostranslate.translate
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# 1. KONFIGURACJA I STYLIZACJA
# ============================================================
st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="centered")
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextInput > div > div > input { background-color: #1a1a1a; color: #dcdcdc; border: 1px solid #333; }
    .stSuccess { background-color: #050505; border: 1px solid #2e7d32; color: #dcdcdc; font-size: 1.2rem; }
    </style>
    """, unsafe_allow_html=True)

# ============================================================
# 2. INICJALIZACJA ARGOS (BEZ LIMITÓW)
# ============================================================
@st.cache_resource
def setup_translator():
    try:
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()
        package_to_install = next(filter(lambda x: x.from_code == 'pl' and x.to_code == 'en', available_packages), None)
        if package_to_install:
            argostranslate.package.install_from_path(package_to_install.download())
        return True
    except: return False

translator_ready = setup_translator()

# ============================================================
# 3. ŁADOWANIE BAZY DANYCH
# ============================================================
@st.cache_data
def load_data():
    def read_json(fn):
        if not os.path.exists(fn): return []
        with open(fn, "r", encoding="utf-8") as f: return json.load(f)
    
    osnova = read_json("osnova.json")
    vuzor = read_json("vuzor.json")
    
    # Indeksowanie dla szybkiego szukania
    dic = {}
    for entry in osnova:
        pl = entry.get("polish", "").lower().strip()
        if pl:
            if pl not in dic: dic[pl] = []
            dic[pl].append(entry)
    return dic, vuzor

dictionary, vuzor_data = load_data()

# ============================================================
# 4. FUNKCJE LOGICZNE (TWOJE ZASADY)
# ============================================================

def apply_case_format(original, translated):
    """Zachowuje wielkość liter (Case-by-Case)"""
    if original.isupper(): return translated.upper()
    if original.istitle(): return translated.capitalize()
    return translated.lower()

def fix_word_order(words_with_pos):
    """ZASADA: Przymiotnik ZAWSZE przed rzeczownikiem"""
    result = []
    i = 0
    while i < len(words_with_pos):
        # Jeśli znajdziemy Rzeczownik, a po nim Przymiotnik (polska kolejność)
        if i + 1 < len(words_with_pos):
            w1, pos1 = words_with_pos[i]
            w2, pos2 = words_with_pos[i+1]
            
            if "noun" in pos1.lower() and "adj" in pos2.lower():
                # Zamieniamy kolejność: Przymiotnik -> Rzeczownik
                result.append(w2)
                result.append(w1)
                i += 2
                continue
        result.append(words_with_pos[i][0])
        i += 1
    return result

def translate_text(text):
    # Czyszczenie i rozbicie na słowa
    raw_words = text.split()
    translated_sentence = []
    matches_found = []

    for word in raw_words:
        clean_word = re.sub(r'[^\w]', '', word).lower()
        
        # 1. Szukaj w osnova.json
        if clean_word in dictionary:
            entry = dictionary[clean_word][0]
            slov_word = entry['slovian']
            pos = entry.get('type and case', '')
            
            final_word = apply_case_format(word, slov_word)
            translated_sentence.append((final_word, pos))
            matches_found.append(entry)
        else:
            # 2. Fallback do Argos (jeśli brak w bazie)
            try:
                argos_res = argostranslate.translate.translate(word, 'pl', 'en')
                translated_sentence.append((apply_case_format(word, argos_res), "unknown"))
            except:
                translated_sentence.append((word, "unknown"))

    # 3. Zastosuj zmianę kolejności (Przymiotnik przed Rzeczownik)
    ordered_words = fix_word_order(translated_sentence)
    
    return " ".join(ordered_words), matches_found

# ============================================================
# 5. INTERFEJS
# ============================================================
st.title("Perkladačь slověnьskogo ęzyka")
st.caption("Działanie lokalne (Argos) z Twoją bazą JSON")

user_input = st.text_input("Vupiši rěčenьje:", placeholder="np. Wojsko Słowiańskie")

if user_input:
    if not translator_ready:
        st.warning("Inicjalizacja silnika...")
    else:
        with st.spinner("Przekładanie..."):
            result, matches = translate_text(user_input)
            
            st.markdown("### Vynik perklada:")
            st.success(result)
            
            if matches:
                with st.expander("Užito jiz osnovy (RAG)"):
                    for m in matches:
                        st.write(f"**{m['polish']}** → `{m['slovian']}`")
