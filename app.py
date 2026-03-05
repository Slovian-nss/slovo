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
# 2. INICJALIZACJA SILNIKA (LOKALNIE)
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
# 3. ŁADOWANIE TWOJEJ BAZY (OSNOVA I VUZOR)
# ============================================================
@st.cache_data
def load_data():
    def read_json(fn):
        if not os.path.exists(fn): return []
        with open(fn, "r", encoding="utf-8") as f: return json.load(f)
    
    osnova = read_json("osnova.json")
    vuzor = read_json("vuzor.json")
    
    dic = {}
    for entry in osnova:
        pl = entry.get("polish", "").lower().strip()
        if pl:
            if pl not in dic: dic[pl] = []
            dic[pl].append(entry)
    return dic, vuzor

dictionary, vuzor_data = load_data()

# ============================================================
# 4. LOGIKA WYMUSZAJĄCA TWOJE ZASADY (KOD ZAMIAST PROMPTU)
# ============================================================

def match_case(original, translated):
    """Zasada Case-by-Case: Matka -> Mati, matka -> mati"""
    if original.isupper(): return translated.upper()
    if original[0].isupper(): return translated.capitalize()
    return translated.lower()

def reorder_grammar(words_with_info):
    """KRYTYCZNA ZASADA: Przymiotnik ZAWSZE przed rzeczownikiem"""
    result = []
    i = 0
    while i < len(words_with_info):
        # Sprawdzamy, czy mamy parę: Rzeczownik + Przymiotnik (polska kolejność)
        if i + 1 < len(words_with_info):
            w1, info1 = words_with_info[i]
            w2, info2 = words_with_info[i+1]
            
            # Jeśli w1 to rzeczownik (noun), a w2 to przymiotnik (adj) -> zamień kolejność
            if "noun" in info1.get('type', '') and "adj" in info2.get('type', ''):
                result.append(w2)
                result.append(w1)
                i += 2
                continue
        
        result.append(words_with_info[i][0])
        i += 1
    return result

def custom_translate(text):
    # 1. Czyszczenie i rozbicie na słowa
    words = text.split()
    processed_sentence = []
    found_in_base = []

    for word in words:
        clean = re.sub(r'[^\w]', '', word).lower()
        
        # 2. Szukanie w Twojej bazie (OSNOVA)
        if clean in dictionary:
            entry = dictionary[clean][0]
            slov_word = entry['slovian']
            # Zapamiętujemy typ słowa do późniejszej zmiany kolejności
            word_type = entry.get('type and case', '').lower()
            
            final_word = match_case(word, slov_word)
            processed_sentence.append((final_word, {'type': word_type}))
            found_in_base.append(entry)
        else:
            # 3. Fallback do Argos (jeśli brak w bazie)
            try:
                translated = argostranslate.translate.translate(word, 'pl', 'en')
                processed_sentence.append((match_case(word, translated), {'type': 'unknown'}))
            except:
                processed_sentence.append((word, {'type': 'unknown'}))

    # 4. WYMUSZENIE KOLEJNOŚCI: Przymiotnik przed Rzeczownik
    final_ordered_words = reorder_grammar(processed_sentence)
    
    return " ".join(final_ordered_words), found_in_base

# ============================================================
# 5. INTERFEJS UŻYTKOWNIKA
# ============================================================
st.title("Perkladačь slověnьskogo ęzyka")
st.caption("Działanie lokalne (Argos + Logika Gramatyczna) - Bez Limitów")

user_input = st.text_input("Vupiši rěčenьje:", placeholder="np. Wojsko Słowiańskie")

if user_input:
    if not translator_ready:
        st.info("Inicjalizacja silnika...")
    else:
        with st.spinner("Przetwarzanie zasad gramatyki..."):
            result, matches = custom_translate(user_input)
            
            st.markdown("### Vynik perklada:")
            st.success(result)
            
            if matches:
                with st.expander("Užito jiz Twojej podstawy (RAG)"):
                    for m in matches:
                        st.write(f"**{m['polish']}** → `{m['slovian']}` ({m.get('type and case','')})")
