import streamlit as st
import json
import os
import re
from groq import Groq

# ============================================================
# 1. KONFIGURACJA I STYLIZACJA
# ============================================================
st.set_page_config(page_title="Perkladačь slověnьskogo ęzyka", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextInput > div > div > input { background-color: #1a1a1a; color: #dcdcdc; border: 1px solid #333; }
    .stSuccess { background-color: #050505; border: 1px solid #2e7d32; color: #dcdcdc; font-size: 1.2rem; }
    .stCaption { color: #888; }
    </style>
    """, unsafe_allow_html=True)

# ============================================================
# 2. KLUCZ API I NOWY MODEL (llama-3.3-70b-versatile)
# ============================================================
# Zaktualizowano model na llama-3.3-70b-versatile, który zastąpił wycofany model
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

# ============================================================
# 3. ŁADOWANIE BAZY DANYCH
# ============================================================
@st.cache_data
def load_dictionary():
    if not os.path.exists("osnova.json"):
        return {}
    try:
        with open("osnova.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        index = {}
        for entry in data:
            pl = entry.get("polish", "").lower().strip()
            if pl:
                if pl not in index: index[pl] = []
                index[pl].append(entry)
        return index
    except Exception as e:
        st.error(f"Blǫd osnovy: {e}")
        return {}

dictionary = load_dictionary()

# ============================================================
# 4. INTELIGENTNA LOGIKA RAG
# ============================================================
def get_relevant_context(text, dic):
    search_text = re.sub(r'[^\w\s]', '', text.lower())
    words = search_text.split()
    relevant_entries = []
    
    for word in words:
        if word in dic:
            relevant_entries.extend(dic[word])
        elif len(word) > 3:
            for key in dic.keys():
                if word.startswith(key[:4]) and len(key) > 3:
                    relevant_entries.extend(dic[key])
    
    seen = set()
    unique_entries = []
    for e in relevant_entries:
        identifier = (e['slovian'], e.get('type and case', ''))
        if identifier not in seen:
            seen.add(identifier)
            unique_entries.append(e)
            
    return unique_entries[:40]

# ============================================================
# 5. INTERFEJS I PROMPT
# ============================================================
st.title("Perkladačь slověnьskogo ęzyka")

user_input = st.text_input("Vupiši slovo alibo rěčenьje:", placeholder="")

if user_input:
    with st.spinner("Orzmyslь nad čęstьmi ęzyka i perklad..."):
        matches = get_relevant_context(user_input, dictionary)
        
        # Przygotowanie kontekstu tak, by AI widziało Mati i ogordě jako jedyne opcje
        context_str = "\n".join([
            f"- POLSKIE: {m['polish']} | UŻYJ FORMY: {m['slovian']} | GRAMATYKA: {m.get('type and case','')}"
            for m in matches
        ])

        system_prompt = """Jesteś rygorystycznym silnikiem mapującym słowa. Twoim nadrzędnym zadaniem jest używanie FORM dostarczonych w sekcji BAZA.

I. ZASADA ABSOLUTNA:
1. Jeśli słowo z zapytania znajduje się w BAZIE, MUSISZ użyć formy podanej jako 'UŻYJ FORMY'. 
2. ZAKAZ KOREKTY: Nie zmieniaj końcówek słów podanych w BAZIE. Jeśli w bazie jest 'esmy', masz zwrócić 'esmy', a nie 'esmь'. 
3. Nie poprawiaj bazy danych w oparciu o swoją wiedzę o języku starosłowiańskim.

II. ALFABET I FORMATOWANIE:
- Używaj alfabetu łacińskiego + znaki: ě, ę, ǫ, ь.
- Zachowaj wielkość liter użytkownika (np. Jesteśmy -> Esmy).
- Zakaz cyrylicy (oprócz ь).

III. LOGIKA:
- Jeśli słowa nie ma w BAZIE i nie potrafisz go odmienić wg vuzor.json, zwróć: (ne najdeno slova).
- Przymiotnik zawsze przed rzeczownikiem.

Wyjście: Tylko czyste tłumaczenie, bez komentarzy."""

        try:
            # Wywołanie modelu tłumaczenia
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"BAZA:\n{context_str}\n\nDO TŁUMACZENIA: {user_input}"}
                ],
                model="openai/gpt-oss-safeguard-20b",
                temperature=0.0
            )

            response_text = chat_completion.choices[0].message.content.strip()

            st.markdown("### Vynik perklada:")
            st.success(response_text)

            if matches:
                with st.expander("Užito žerdlo jiz osnovy"):
                    for m in matches:
                        st.write(f"**{m['polish']}** → `{m['slovian']}` ({m.get('type and case','')})")

        except Exception as e:
            st.error(f"Blǫd umětьnogo uma: {e}")












