import streamlit as st

def apply_custom_style():
    """Aplikuje style CSS do aplikacji Streamlit."""
    st.markdown("""
    <style>
        /* Główne tło i marginesy */
        .stApp { margin-top: -50px; background:#f0f2f5; }
        
        .title-text {
            color:#002b49;
            font-weight:800;
            text-align:center;
            font-size:2.2rem;
            margin-bottom: 20px !important;
        }

        /* Wyrównanie pionowe rzędu wyboru języka */
        [data-testid="stHorizontalBlock"] {
            align-items: center !important;
            gap: 0.5rem !important;
        }

        /* Stylizacja list rozwijanych */
        div[data-baseweb="select"] {
            border: 2px solid #2d3748 !important;
            border-radius: 10px !important;
            background: white !important;
        }

        /* Przyciski funkcyjne (Wklej/Kopiuj) */
        .stButton button {
            background:#002b49 !important;
            color:white !important;
            border-radius:6px !important;
            height: 32px !important;
            font-size: 14px !important;
            padding: 0px 15px !important;
            width: auto !important;
        }

        /* Przycisk zamiany języków (⇄) */
        .swap-btn-container button {
            width: 50px !important;
            height: 40px !important;
            font-size: 20px !important;
        }

        /* Pola tekstowe */
        .stTextArea textarea {
            border:2px solid #2d3748 !important;
            border-radius:10px !important;
            padding: 15px !important;
            background: white !important;
        }
        
        .row-spacer { margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    """Renderuje nagłówek strony."""
    st.markdown('<h1 class="title-text">Tłumacz Języka Słowiańskiego (Prasłowiańskiego)</h1>', unsafe_allow_html=True)
