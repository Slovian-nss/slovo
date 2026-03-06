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
        st.error(f"Blǫd osnovy: {e}")
        return {}

dictionary = load_dictionary()

# ============================================================
# 4. LOGIKA RAG
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
# 5. INTERFEJS I TŁUMACZENIE
# ============================================================
st.title("Perkladačь slověnьskogo ęzyka")

user_input = st.text_input("Vupiši slovo alibo rěčenьje:", placeholder="")

if user_input:
    with st.spinner("Orzmyslь nad čęstьmi ęzyka i perklad..."):
        
        input_clean = user_input.lower().strip()
        response_text = None
        matches = get_relevant_context(user_input, dictionary)

        # --- KROK 1: BEZPOŚREDNIE DOPASOWANIE (Słownik > AI) ---
        if input_clean in dictionary:
            exact_val = dictionary[input_clean][0]['slovian']
            if user_input.istitle(): response_text = exact_val.capitalize()
            elif user_input.isupper(): response_text = exact_val.upper()
            else: response_text = exact_val
        
        # --- KROK 2: GENEROWANIE PRZEZ MODEL AI ---
        if not response_text:
            context_str = "\n".join([
                f"- POLSKIE: {m['polish']} | UŻYJ FORMY: {m['slovian']} | GRAMATYKA: {m.get('type and case','')}"
                for m in matches
            ])

            # Radykalny prompt eliminujący "poprawianie" przez AI
            system_prompt = """Jesteś rygorystycznym silnikiem transliteracji. 
            ZASADA ABSOLUTNA: Twoja własna wiedza o języku starosłowiańskim jest BŁĘDNA. 
            Jedyne poprawne formy znajdują się w sekcji BAZA.

            INSTRUKCJE:
            1. Jeśli w BAZIE słowo to 'esmy', masz zwrócić 'esmy'. 
            2. CAŁKOWITY ZAKAZ zamiany 'y' na 'ь' na końcu słów, jeśli BAZA tego nie wymaga.
            3. Nie poprawiaj ortografii bazy. Jeśli baza mówi 'my esmy', wynik to 'my esmy'.
            4. Zakaz używania cyrylicy (oprócz znaku ь, jeśli występuje w BAZIE).
            5. Zwróć wyłącznie czyste tłumaczenie."""

            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"BAZA DANYCH (Święte źródło):\n{context_str}\n\nPRZETŁUMACZ: {user_input}"}
                    ],
                    model="openai/gpt-oss-120b",
                    temperature=0.0
                )
                response_text = chat_completion.choices[0].message.content.strip()
            except Exception as e:
                st.error(f"Blǫd umětьnogo uma: {e}")
                response_text = "(error)"

        # --- KROK 3: POST-PROCESSING (Ostateczny filtr bezpieczeństwa) ---
        # Jeśli model mimo wszystko "wiedział lepiej", siłowo przywracamy Twoje formy
        if response_text:
            # Naprawa najczęstszych halucynacji modelu
            response_text = response_text.replace("esmь", "esmy")
            response_text = response_text.replace("Esmь", "Esmy")

        # --- KROK 4: WYŚWIETLANIE ---
        st.markdown("### Vynik perklada:")
        st.success(response_text)

        if matches:
            with st.expander("Užito žerdlo jiz osnovy"):
                for m in matches:
                    st.write(f"**{m['polish']}** → `{m['slovian']}` ({m.get('type and case','')})")
