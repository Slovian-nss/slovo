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
    </style>
    """, unsafe_allow_html=True)

# ============================================================
# 2. KONFIGURACJA KLIENTA GROQ
# ============================================================
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
        st.error(f"Błąd bazy: {e}")
        return {}

dictionary = load_dictionary()

# ============================================================
# 4. PRECYZYJNA LOGIKA POBIERANIA KONTEKSTU
# ============================================================
def get_strict_context(text, dic):
    search_text = re.sub(r'[^\w\s]', '', text.lower())
    words = search_text.split()
    relevant_entries = []
    
    for word in words:
        if word in dic:
            relevant_entries.extend(dic[word])
    
    # Usuwanie duplikatów
    seen = set()
    unique_entries = []
    for e in relevant_entries:
        identifier = (e['polish'], e['slovian'])
        if identifier not in seen:
            seen.add(identifier)
            unique_entries.append(e)
            
    return unique_entries

# ============================================================
# 5. INTERFEJS I TŁUMACZENIE
# ============================================================
st.title("Perkladačь slověnьskogo ęzyka")

user_input = st.text_input("Vupiši slovo alibo rěčenьje:", placeholder="")

if user_input:
    with st.spinner("Kopiowanie z bazy..."):
        matches = get_strict_context(user_input, dictionary)
        
        # Przygotowanie kontekstu jako sztywnego słownika mapowania
        mapping_list = "\n".join([
            f"ZASADA: Jeśli widzisz polskie słowo '{m['polish']}', to MUSISZ napisać dokładnie: '{m['slovian']}'"
            for m in matches
        ])

        # NOWY PROMPT: Blokada kreatywności AI
        system_prompt = """Jesteś prostym automatem podstawiającym słowa. Nie jesteś lingwistą. 
Twoja wiedza o językach nie istnieje. Twoim jedynym zadaniem jest wykonanie operacji 'znajdź i zamień' na podstawie dostarczonych ZASAD.

INSTRUKCJA:
1. Przeczytaj tekst do tłumaczenia.
2. Znajdź odpowiednie słowo w dostarczonych ZASADACH.
3. Skopiuj formę słowiańską litera po literze. Nie zmieniaj końcówek!
4. Jeśli w ZASADZIE jest 'esmy', piszesz 'esmy'. Jeśli w ZASADZIE jest 'jesmь', piszesz 'jesmь'.
5. Nigdy nie używaj swojej pamięci, używaj tylko tekstu z ZASAD.
6. Nie dodawaj żadnych komentarzy."""

        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"ZASADY MAPOWANIA:\n{mapping_list}\n\nTEKST DO ZAMIANY: {user_input}"}
                ],
                model="openai/gpt-oss-120b",
                temperature=0.0
            )
            response_text = chat_completion.choices[0].message.content.strip()

            # Usuwanie ewentualnych cudzysłowów, które AI czasem dodaje
            response_text = re.sub(r'^["\']|["\']$', '', response_text)

            st.markdown("### Vynik perklada:")
            st.success(response_text)

        except Exception as e:
            st.error(f"Błąd połączenia: {e}")

        if matches:
            with st.expander("Użyte dane z osnova.json"):
                for m in matches:
                    st.write(f"W bazie: **{m['polish']}** → `{m['slovian']}`")
