import streamlit as st
import json
import os
import re
from collections import defaultdict
from groq import Groq

# Konfiguracja strony
st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="centered")

st.markdown("""
<style>
.main {background:#0e1117}
.stTextArea textarea {background:#1a1a1a;color:#dcdcdc}
</style>
""", unsafe_allow_html=True)

# ================== GROQ ==================

# Upewnij się, że masz klucz w .streamlit/secrets.toml
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Błąd konfiguracji klucza API. Sprawdź st.secrets.")

# ================== ŁADOWANIE DANYCH ==================

@st.cache_data
def load_json(filename):
    if not os.path.exists(filename):
        return []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

osnova = load_json("osnova.json")
vuzor = load_json("vuzor.json")

# ================== INDEKS SŁOWNIKA ==================

@st.cache_data
def build_dictionary(data):
    dic = defaultdict(list)
    for entry in data:
        # Zakładamy, że klucz w JSON to "polish", a wynik to "slovian"
        key = entry.get("polish", "").lower().strip()
        if key:
            dic[key].append(entry)
    return dic

dictionary = build_dictionary(osnova)

# ================== WYSZUKIWANIE KONTEKSTOWE ==================

def get_context(text, dic):
    # Wyciąganie słów (usuwanie interpunkcji do wyszukiwania)
    words = re.findall(r'\b\w+\b', text.lower())
    results = []
    seen = set()

    for w in words:
        # 1. Dokładne dopasowanie
        if w in dic:
            for e in dic[w]:
                pair = (e.get("polish"), e.get("slovian"))
                if pair not in seen:
                    results.append(e)
                    seen.add(pair)
        
        # 2. Szukanie po rdzeniu (jeśli słowo długie)
        elif len(w) >= 4:
            pref = w[:4]
            for base, entries in dic.items():
                if base.startswith(pref):
                    for e in entries:
                        pair = (e.get("polish"), e.get("slovian"))
                        if pair not in seen:
                            results.append(e)
                            seen.add(pair)
    return results

# ================== INTERFEJS UŻYTKOWNIKA ==================

st.title("Perkladačь slověnьskogo ęzyka")

user_input = st.text_area(
    "Vupiši slovo alibo rěčenьje:",
    placeholder="Np. W miastach siła.",
    height=150
)

if user_input:
    with st.spinner("Przetwarzanie..."):
        # Pobranie pasujących słówek ze słownika
        matches = get_context(user_input, dictionary)

        # Formułowanie danych dla modelu
        mapping = "\n".join(
            [f"PL '{m.get('polish')}' -> SL '{m.get('slovian')}' (Kategoria: {m.get('category', 'nieznana')})" for m in matches]
        )

        system_prompt = f"""Jesteś precyzyjnym tłumaczem na język prasłowiański.
Używasz WYŁĄCZNIE słów dostarczonych w DANYCH SŁOWNIKOWYCH.

DANE SŁOWNIKOWE:
{mapping}

PRZYKŁADOWE WZORY ODMIAN:
{json.dumps(vuzor[:15], ensure_ascii=False)}

ZASADY BEZWZGLĘDNE:
1. Jeśli w danych słownikowych nie ma odpowiednika dla słowa, wstaw "(ne najdeno slova)" i tłumacz dalej.
2. SZYK: Przymiotniki (adjective) i przysłówki (adverb) ZAWSZE przed rzeczownikami (noun).
3. FORMAT: Zachowaj oryginalną interpunkcję, wielkość liter i układ tekstu. 
4. Nie dodawaj żadnego komentarza od siebie, tylko czyste tłumaczenie."""

        try:
            # POPRAWKA: Zmiana modelu na istniejący w Groq (np. llama-3.3-70b-versatile lub mixtral-8x7b-32768)
            chat = client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.1,
                max_tokens=1000
            )

            result = chat.choices[0].message.content.strip()

            st.markdown("### Vynik perklada:")
            st.success(result)

        except Exception as e:
            st.error(f"Blǫd perklada: {e}")

# Stopka pomocnicza
if not osnova:
    st.warning("Uwaga: Nie znaleziono pliku osnova.json. Słownik jest pusty.")
