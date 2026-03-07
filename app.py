import streamlit as st
import json
import os
import re
from collections import defaultdict
from groq import Groq

# ================== KONFIGURACJA ==================
st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="centered")

st.markdown("""
<style>
.main {background:#0e1117}
.stTextArea textarea {background:#1a1a1a;color:#dcdcdc;font-size:1.1rem;}
</style>
""", unsafe_allow_html=True)

# Klient Groq (pobierany ze st.secrets)
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ================== ŁADOWANIE DANYCH ==================
@st.cache_data
def load_all_data():
    def load_json(name):
        if not os.path.exists(name): return []
        with open(name, "r", encoding="utf-8") as f: return json.load(f)
    
    # Ładujemy wszystko: osnova i vuzor
    return load_json("vuzor.json") + load_json("osnova.json")

DATA = load_all_data()

# ================== PRZYGOTOWANIE KONTEKSTU DLA LLM ==================

def get_smart_context(text):
    words = re.findall(r'\w+', text.lower())
    relevant_entries = []
    seen = set()

    for w in words:
        # Szukamy wszystkiego, co pasuje do słowa lub jego rdzenia
        stem = w[:4] if len(w) >= 4 else w
        for entry in DATA:
            pl = entry.get("polish", "").lower()
            # Dodajemy tylko jeśli polskie słowo pasuje lub zaczyna się tak samo
            if w == pl or (len(w) >= 4 and pl.startswith(stem)):
                # Tworzymy unikalny klucz, by nie dublować identycznych wpisów
                key = (entry['polish'], entry['slovian'], entry.get('type and case', ''))
                if key not in seen:
                    relevant_entries.append(entry)
                    seen.add(key)
    return relevant_entries

# ================== INTERFEJS I LOGIKA HYBRYDOWA ==================

st.title("Perkladačь slověnьskogo ęzyka")
st.subheader("Silnik Hybrydowy: Baza danych + Groq AI")

user_input = st.text_area("Vupiši rěčenьje:", placeholder="Np. W moim ogrodzie są ludzie.", height=150)

if user_input:
    with st.spinner("Analiza gramatyczna i tłumaczenie..."):
        # 1. Wyciągamy pasujące rekordy z Twoich plików JSON
        matches = get_smart_context(user_input)
        
        # 2. Formatujemy dane dla AI tak, by wiedziało o częściach mowy
        mapping = "\n".join([
            f"- PL: '{m['polish']}' -> SL: '{m['slovian']}' ({m.get('type and case', 'podstawowy')})"
            for m in matches
        ])

        system_prompt = f""" Jesteś ekspertem języka prasłowiańskiego.
Twoim zadaniem jest przetłumaczyć zdanie używając WYŁĄCZNIE form podanych w poniższych danych.

DANE SŁOWNIKOWE (użyj odpowiedniej formy gramatycznej):
{mapping}

ZASADY:
1. Słowo 'w' tłumacz jako 'Vu'.
2. Wybieraj RZECZOWNIKI (noun) dla obiektów, a nie CZASOWNIKI (verb) o podobnym rdzeniu.
3. Jeśli w danych jest forma z 'locative' dla słowa po przyimku 'w', użyj jej (np. obgordě).
4. Jeśli słowa nie ma w danych, napisz (ne najdeno slova).
5. Wynik ma zawierać TYLKO przetłumaczone zdanie, bez komentarzy. """

        try:
            chat = client.chat.completions.create(
                model="llama-3.3-70b-versatile", # Najlepszy model na Groq do języków słowiańskich
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Przetłumacz: {user_input}"}
                ],
                temperature=0 # Zerowa kreatywność = trzymanie się Twoich tabel
            )

            result = chat.choices[0].message.content.strip()

            st.markdown("### Vynik perklada:")
            st.success(result)

        except Exception as e:
            st.error(f"Błąd API: {e}")

    with st.expander("Zobacz dane przekazane do AI"):
        st.write("To są rekordy, które AI dostało do wyboru z Twoich plików JSON:")
        st.json(matches)
