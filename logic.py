from deep_translator import GoogleTranslator

def translate_text(text, src_lang, tgt_lang):
    """
    Tłumaczy tekst używając biblioteki deep-translator.
    Język 'sl' (prasłowiański) nie jest wspierany przez Google, 
    więc tymczasowo mapujemy go na inny lub zostawiamy placeholder.
    """
    if not text.strip():
        return ""
    
    try:
        # Mapowanie Twoich skrótów na obsługiwane przez Google
        # Jeśli wybierzesz 'sl', Google go nie zrozumie, więc użyjemy np. 'sk' (słowacki) 
        # lub po prostu zwrócimy tekst, jeśli to ma być Twój własny algorytm.
        
        supported_src = "auto" if src_lang == "sl" else src_lang
        supported_tgt = "pl" if tgt_lang == "sl" else tgt_lang # Placeholder dla prasłowiańskiego
        
        translation = GoogleTranslator(source=supported_src, target=supported_tgt).translate(text)
        return translation
    except Exception as e:
        return f"Błąd tłumaczenia: {str(e)}"

def get_languages():
    return {
        "pl": "Polski",
        "en": "Angielski",
        "de": "Niemiecki",
        "fr": "Francuski",
        "es": "Hiszpański",
        "ru": "Rosyjski",
        "sl": "Prasłowiański (Beta)"
    }
