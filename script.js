let plToSlo = {}, sloToPl = {};
let wordTypes = {};

const languageData = [
    // Twoje oryginalne wpisy (bez zmian)
    { code: 'slo', pl: 'Słowiański', en: 'Slovian (Slavic)', slo: 'Slověnьsky', de: 'Slawisch' },
    { code: 'en', pl: 'Angielski', en: 'English', slo: "Angol'ьsky", de: 'Englisch' },
    { code: 'pl', pl: 'Polski', en: 'Polish', slo: "Pol'ьsky", de: 'Polnisch' },
    { code: 'de', pl: 'Niemiecki', en: 'German', slo: 'Nemьčьsky', de: 'Deutsch' },
    { code: 'cs', pl: 'Czeski', en: 'Czech', slo: 'Češьsky', de: 'Tschechisch' },
    { code: 'sk', pl: 'Słowacki', en: 'Slovak', slo: 'Slovačьsky', de: 'Slowakisch' },
    { code: 'ru', pl: 'Rosyjski', en: 'Russian', slo: 'Rusьsky', de: 'Russisch' },
    { code: 'fr', pl: 'Francuski', en: 'French', slo: 'Franьsky', de: 'Französisch' },
    { code: 'es', pl: 'Hiszpański', en: 'Spanish', slo: 'Španьsky', de: 'Spanisch' },
    { code: 'it', pl: 'Włoski', en: 'Italian', slo: 'Volšьsky', de: 'Italienisch' },
    { code: 'uk', pl: 'Ukraiński', en: 'Ukrainian', slo: 'Ukrajinьsky', de: 'Ukrainisch' },
    { code: 'af', pl: 'Afrikaans', en: 'Afrikaans', slo: 'Južьnozemьsky', de: 'Afrikaans' },
    { code: 'sq', pl: 'Albański', en: 'Albanian', slo: 'Albanьsky', de: 'Albanisch' },
    { code: 'am', pl: 'Amharski', en: 'Amharic', slo: 'Amharьsky', de: 'Amharisch' },
    { code: 'ar', pl: 'Arabski', en: 'Arabic', slo: 'Arabьsky', de: 'Arabisch' },
    { code: 'az', pl: 'Azerbejdżański', en: 'Azerbaijani', slo: "Azerbed'ěnьsky", de: 'Aserbaidschanisch' },
    { code: 'bn', pl: 'Bengalski', en: 'Bengali', slo: 'Bengalьsky', de: 'Bengalis' },
    { code: 'be', pl: 'Białoruski', en: 'Belarusian', slo: 'Bělorusьsky', de: 'Weißrussisch' },
    { code: 'bg', pl: 'Bułgarski', en: 'Bulgarian', slo: "Boulgar'ьsky", de: 'Bulgarisch' },
    { code: 'ca', pl: 'Kataloński', en: 'Catalan', slo: "Katalonьsky", de: 'Katalanisch' },
    { code: 'zh-CN', pl: 'Chiński (uproszczony)', en: 'Chinese (Simplified)', slo: 'Kitajьsky (Uproščeny)', de: 'Chinesisch (Vereinfacht)' },
    { code: 'zh-TW', pl: 'Chiński (tradycyjny)', en: 'Chinese (Traditional)', slo: 'Kitajьsky (Obyčajьny)', de: 'Chinesisch (Traditionell)' },
    { code: 'hr', pl: 'Chorwacki', en: 'Croatian', slo: 'Horvatьsky', de: 'Kroatisch' },
    { code: 'da', pl: 'Duński', en: 'Danish', slo: 'Dunьsky', de: 'Dänisch' },
    { code: 'nl', pl: 'Holenderski', en: 'Dutch', slo: 'Niskozemьsky', de: 'Niederländisch' },
    { code: 'et', pl: 'Estoński', en: 'Estonian', slo: 'Estonьsky', de: 'Estnisch' },
    { code: 'fi', pl: 'Fiński', en: 'Finnish', slo: 'Finьsky', de: 'Finnisch' },
    { code: 'gl', pl: 'Galicyjski', en: 'Galician', slo: 'Galicijьski', de: 'Galizisch' },
    { code: 'el', pl: 'Grecki', en: 'Greek', slo: 'Grečьsky', de: 'Griechisch' },
    { code: 'hi', pl: 'Hindi', en: 'Hindi', slo: 'Hindьsky', de: 'Hindi' },
    { code: 'hu', pl: 'Węgierski', en: 'Hungarian', slo: 'Ǫgrinьsky', de: 'Ungarisch' },
    { code: 'is', pl: 'Islandzki', en: 'Icelandic', slo: 'Ledozemьsky', de: 'Isländisch' },
    { code: 'id', pl: 'Indonezyjski', en: 'Indonesian', slo: 'Indonezijьsky', de: 'Indonesisch' },
    { code: 'ga', pl: 'Irlandzki', en: 'Irish', slo: 'Irьsky', de: 'Irisch' },
    { code: 'ja', pl: 'Japoński', en: 'Japanese', slo: 'Japonьsky', de: 'Japanisch' },
    { code: 'ko', pl: 'Koreański', en: 'Korean', slo: 'Koreanьsky', de: 'Koreanisch' },
    { code: 'lv', pl: 'Łotewski', en: 'Latvian', slo: 'Latyšьsky', de: 'Lettisch' },
    { code: 'lt', pl: 'Litewski', en: 'Lithuanian', slo: 'Litovьsky', de: 'Litauisch' },
    { code: 'mk', pl: 'Macedoński', en: 'Macedonian', slo: 'Makedonьsky', de: 'Mazedonisch' },
    { code: 'ms', pl: 'Malajski', en: 'Malay', slo: 'Malajьsky', de: 'Malaiisch' },
    { code: 'no', pl: 'Norweski', en: 'Norwegian', slo: 'Norvežьsky', de: 'Norwegisch' },
    { code: 'pt', pl: 'Portugalski', en: 'Portuguese', slo: "Portugal'ьsky", de: 'Portugiesisch' },
    { code: 'ro', pl: 'Rumuński', en: 'Romanian', slo: "Rumunьsky", de: 'Rumänisch' },
    { code: 'sr', pl: 'Serbski', en: 'Serbian', slo: 'Sirbьsky', de: 'Serbisch' },
    { code: 'sl', pl: 'Słoweński', en: 'Slovenian', slo: 'Slovenečьsky', de: 'Slowenisch' },
    { code: 'sv', pl: 'Szwedzki', en: 'Swedish', slo: 'Švedьsky', de: 'Schwedisch' },
    { code: 'th', pl: 'Tajski', en: 'Thai', slo: 'Tajьsky', de: 'Thailändisch' },
    { code: 'tr', pl: 'Turecki', en: 'Turkish', slo: 'Turečьsky', de: 'Türkisch' },
    { code: 'vi', pl: 'Wietnamski', en: 'Vietnamese', slo: 'Větnamьsky', de: 'Vietnamesisch' },
    // Dopisane pozostałe języki Google Translate
    { code: 'hy', pl: 'Ormiański', en: 'Armenian', slo: 'Armenьsky', de: 'Armenisch' },
    { code: 'eu', pl: 'Baskijski', en: 'Basque', slo: 'Baskьsky', de: 'Baskisch' },
    { code: 'bs', pl: 'Bośniacki', en: 'Bosnian', slo: 'Bosnьsky', de: 'Bosnisch' },
    { code: 'cy', pl: 'Walijski', en: 'Welsh', slo: 'Valijьsky', de: 'Walisisch' },
    { code: 'eo', pl: 'Esperanto', en: 'Esperanto', slo: 'Esperanto', de: 'Esperanto' },
    { code: 'ka', pl: 'Gruziński', en: 'Georgian', slo: 'Gruzinьsky', de: 'Georgisch' },
    { code: 'gu', pl: 'Gudżarati', en: 'Gujarati', slo: 'Gudžaratьsky', de: 'Gujarati' },
    { code: 'ha', pl: 'Hausa', en: 'Hausa', slo: 'Hausa', de: 'Hausa' },
    { code: 'he', pl: 'Hebrajski', en: 'Hebrew', slo: 'Hebrějskьsky', de: 'Hebräisch' },
    { code: 'iw', pl: 'Hebrajski (stary kod)', en: 'Hebrew', slo: 'Hebrějskьsky', de: 'Hebräisch' },
    { code: 'ig', pl: 'Igbo', en: 'Igbo', slo: 'Igbo', de: 'Igbo' },
    { code: 'jw', pl: 'Jawajski', en: 'Javanese', slo: 'Javanьsky', de: 'Javanisch' },
    { code: 'kn', pl: 'Kannada', en: 'Kannada', slo: 'Kannada', de: 'Kannada' },
    { code: 'kk', pl: 'Kazachski', en: 'Kazakh', slo: 'Kazahьsky', de: 'Kasachisch' },
    { code: 'km', pl: 'Khmer', en: 'Khmer', slo: 'Khmer', de: 'Khmer' },
    { code: 'lo', pl: 'Laotański', en: 'Lao', slo: 'Laosьsky', de: 'Laotisch' },
    { code: 'la', pl: 'Łacina', en: 'Latin', slo: 'Latinьsky', de: 'Latein' },
    { code: 'mt', pl: 'Maltański', en: 'Maltese', slo: 'Maltanьsky', de: 'Maltesisch' },
    { code: 'mi', pl: 'Maoryski', en: 'Maori', slo: 'Maori', de: 'Maori' },
    { code: 'mr', pl: 'Marathi', en: 'Marathi', slo: 'Marathi', de: 'Marathi' },
    { code: 'mn', pl: 'Mongolski', en: 'Mongolian', slo: 'Mongolьsky', de: 'Mongolisch' },
    { code: 'ne', pl: 'Nepalski', en: 'Nepali', slo: 'Nepalьsky', de: 'Nepalesisch' },
    { code: 'pa', pl: 'Pendżabski', en: 'Punjabi', slo: 'Pendžabьsky', de: 'Panjabi' },
    { code: 'fa', pl: 'Perski', en: 'Persian', slo: 'Persьsky', de: 'Persisch' },
    { code: 'so', pl: 'Somalijski', en: 'Somali', slo: 'Somalьsky', de: 'Somali' },
    { code: 'sw', pl: 'Suahili', en: 'Swahili', slo: 'Suahili', de: 'Suaheli' },
    { code: 'ta', pl: 'Tamilski', en: 'Tamil', slo: 'Tamilьsky', de: 'Tamilisch' },
    { code: 'te', pl: 'Telugu', en: 'Telugu', slo: 'Telugu', de: 'Telugu' },
    { code: 'ur', pl: 'Urdu', en: 'Urdu', slo: 'Urdu', de: 'Urdu' },
    { code: 'zu', pl: 'Zuluski', en: 'Zulu', slo: 'Zulu', de: 'Zulu' }
];

const uiTranslations = {
    // Twoje oryginalne (bez zmian)
    slo: { title: "Slovo Perkladačь", from: "Jiz ęzyka:", to: "Na ęzyk:", paste: "Vyloži", clear: "Terbi", copy: "Poveli", placeholder: "Piši tu..." },
    pl: { title: "Slovo Tłumacz", from: "Z języka:", to: "Na język:", paste: "Wklej", clear: "Usuń", copy: "Kopiuj", placeholder: "Wpisz tekst..." },
    en: { title: "Slovo Translator", from: "From language:", to: "To language:", paste: "Paste", clear: "Clear", copy: "Copy", placeholder: "Type here..." },
    de: { title: "Slovo Übersetzer", from: "Von:", to: "Nach:", paste: "Einfügen", clear: "Löschen", copy: "Kopieren", placeholder: "Text eingeben..." },
    fr: { title: "Traducteur Slovo", from: "De :", to: "Vers :", paste: "Coller", clear: "Effacer", copy: "Copier", placeholder: "Entrez le texte..." },
    es: { title: "Traductor Slovo", from: "De:", to: "A:", paste: "Pegar", clear: "Borrar", copy: "Copiar", placeholder: "Escribe texto..." },
    it: { title: "Traduttore Slovo", from: "Da:", to: "A:", paste: "Incolla", clear: "Cancella", copy: "Copia", placeholder: "Inserisci tekst..." },
    pt: { title: "Tradutor Slovo", from: "De:", to: "Para:", paste: "Colar", clear: "Limpar", copy: "Copiar", placeholder: "Digite o texto..." },
    nl: { title: "Slovo Vertaler", from: "Van:", to: "Naar:", paste: "Plakken", clear: "Wissen", copy: "Kopiëren", placeholder: "Voer tekst in..." },
    sv: { title: "Slovo Översättare", from: "Från:", to: "Till:", paste: "Klistra in", clear: "Rensa", copy: "Kopiera", placeholder: "Skriv text..." },
    no: { title: "Slovo Oversetter", from: "Fra:", to: "Till:", paste: "Lim inn", clear: "Fjern", copy: "Kopier", placeholder: "Skriv tekst..." },
    da: { title: "Slovo Oversætter", from: "Fra:", to: "Til:", paste: "Indsæt", clear: "Ryd", copy: "Kopiér", placeholder: "Indtast tekst..." },
    fi: { title: "Slovo Kääntäjä", from: "Lähde:", to: "Kohde:", paste: "Liitä", clear: "Tyhjennä", copy: "Kopioi", placeholder: "Kirjoita teksti..." },
    ru: { title: "Slovo Переводчик", from: "С языка:", to: "На язык:", paste: "Вставить", clear: "Очистить", copy: "Копировать", placeholder: "Введите текст..." },
    uk: { title: "Slovo Перекладач", from: "З мови:", to: "На мову:", paste: "Вставити", clear: "Очистіть", copy: "Копіювати", placeholder: "Введіть текст..." },
    cs: { title: "Slovo Překladač", from: "Z jazyka:", to: "Do jazyka:", paste: "Vložit", clear: "Vymazat", copy: "Kopírovat", placeholder: "Zadejte text..." },
    sk: { title: "Slovo Prekladač", from: "Z jazyka:", to: "Do jazyka:", paste: "Vložiť", clear: "Vymazať", copy: "Kopírovať", placeholder: "Zadajte text..." },
    sl: { title: "Slovo Prevajalnik", from: "Iz:", to: "V:", paste: "Prilepi", clear: "Počisti", copy: "Kopiraj", placeholder: "Vnesi besedilo..." },
    hr: { title: "Slovo Prevoditelj", from: "Iz:", to: "U:", paste: "Zalijepi", clear: "Obriši", copy: "Kopiraj", placeholder: "Unesi tekst..." },
    sr: { title: "Slovo Преводилац", from: "Са:", to: "На:", paste: "Налепи", clear: "Обриши", copy: "Копирај", placeholder: "Унеси текст..." },
    bg: { title: "Slovo Преводач", from: "От:", to: "На:", paste: "Постави", clear: "Изчисти", copy: "Копирай", placeholder: "Въведи текст..." },
    tr: { title: "Slovo Çevirici", from: "Dilden:", to: "Dile:", paste: "Yapıştır", clear: "Temizle", copy: "Kopyala", placeholder: "Metin gir..." },
    el: { title: "Slovo Μεταφραστής", from: "Από:", to: "Προς:", paste: "Επικόλληση", clear: "Καθαρισμός", copy: "Αντιγραφή", placeholder: "Εισάγετε κείμενο..." },
    ro: { title: "Traducător Slovo", from: "Din:", to: "În:", paste: "Lipește", clear: "Șterge", copy: "Copiază", placeholder: "Introdu text..." },
    hu: { title: "Slovo Fordító", from: "Erről:", to: "Erre:", paste: "Beillesztés", clear: "Törlés", copy: "Másolás", placeholder: "Írj szöveget..." },
    zh: { title: "Slovo 翻译器", from: "从:", to: "到:", paste: "粘贴", clear: "清除", copy: "复制", placeholder: "输入文本..." },
    ja: { title: "Slovo 翻訳", from: "元の言語:", to: "翻訳先:", paste: "貼り付け", clear: "クリア", copy: "コピー", placeholder: "テキストを入力..." },
    ko: { title: "Slovo 번역기", from: "출발:", to: "도착:", paste: "붙여넣기", clear: "지우기", copy: "복사", placeholder: "텍스트 입력..." },
    ar: { title: "مترجم Slovo", from: "من:", to: "إلى:", paste: "لصق", clear: "مسح", copy: "نسخ", placeholder: "أدخل النص..." },

    // Nowe tłumaczenia interfejsu dla pozostałych języków z Twojej listy:
    af: { title: "Slovo Vertaler", from: "Van taal:", to: "Na taal:", paste: "Plak", clear: "Vee uit", copy: "Kopieer", placeholder: "Tik hier..." },
    sq: { title: "Slovo Përkthyesi", from: "Nga gjuha:", to: "Në gjuhën:", paste: "Ngjit", clear: "Pastro", copy: "Kopjo", placeholder: "Shkruaj këtu..." },
    am: { title: "Slovo አስተርጓሚ", from: "ከቋንቋ:", to: "ወደ ቋንቋ:", paste: "ለጥፍ", clear: "አጽዳ", copy: "ቅዳ", placeholder: "እዚህ ይፃፉ..." },
    az: { title: "Slovo Tərcüməçi", from: "Dildən:", to: "Dilə:", paste: "Yapışdır", clear: "Təmizlə", copy: "Kopyala", placeholder: "Bura yazın..." },
    bn: { title: "Slovo অনুবাদক", from: "ভাষা থেকে:", to: "ভাষা পর্যন্ত:", paste: "পেস্ট", clear: "পরিষ্কার", copy: "কপি", placeholder: "এখানে লিখুন..." },
    ca: { title: "Traductor Slovo", from: "De la llengua:", to: "A la llengua:", paste: "Enganxa", clear: "Neteja", copy: "Copia", placeholder: "Escriu aquí..." },
    et: { title: "Slovo Tõlkija", from: "Keelest:", to: "Keelde:", paste: "Kleebi", clear: "Puhasta", copy: "Kopeeri", placeholder: "Sisesta tekst..." },
    gl: { title: "Tradutor Slovo", from: "Do idioma:", to: "Ao idioma:", paste: "Pegar", clear: "Limpar", copy: "Copiar", placeholder: "Escribe aquí..." },
    hi: { title: "Slovo अनुवादक", from: "भाषा से:", to: "भाषा तक:", paste: "पेस्ट करें", clear: "साफ़ करें", copy: "कॉपी करें", placeholder: "यहाँ लिखें..." },
    id: { title: "Penerjemah Slovo", from: "Dari bahasa:", to: "Ke bahasa:", paste: "Tempel", clear: "Bersihkan", copy: "Salin", placeholder: "Ketik di sini..." },
    ga: { title: "Slovo Aistritheoir", from: "Ó theanga:", to: "Go teanga:", paste: "Greamaigh", clear: "Glan", copy: "Cóipeáil", placeholder: "Scríobh anseo..." },
    lv: { title: "Slovo Tulkotājs", from: "No valodas:", to: "Uz valodu:", paste: "Ielīmēt", clear: "Notīrīt", copy: "Kopēt", placeholder: "Ievadiet tekstu..." },
    lt: { title: "Slovo Vertėjas", from: "Iš kalbos:", to: "Į kalbą:", paste: "Įklijuoti", clear: "Išvalyti", copy: "Kopijuoti", placeholder: "Įveskite tekstą..." },
    ms: { title: "Penterjemah Slovo", from: "Daripada bahasa:", to: "Kepada bahasa:", paste: "Tampal", clear: "Padam", copy: "Salin", placeholder: "Taip di sini..." },
    vi: { title: "Slovo Phiên dịch", from: "Từ ngôn ngữ:", to: "Sang ngôn ngữ:", paste: "Dán", clear: "Xóa", copy: "Sao chép", placeholder: "Nhập văn bản..." }
};

// --- FUNKCJE WIELKOŚCI LITER ---

function getCase(word) {
    if (!word) return "lower";
    if (word === word.toUpperCase() && word.length > 1) return "upper";
    if (word[0] === word[0].toUpperCase()) return "title";
    return "lower";
}

function applyCase(word, caseType) {
    if (!word) return "";
    switch (caseType) {
        case "upper": return word.toUpperCase();
        case "title": return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
        default: return word.toLowerCase();
    }
}

// --- LOGIKA TŁUMACZENIA ---

function dictReplace(text, dict) {
    if (!text) return "";
    const urlRegex = /(https?:\/\/[^\s]+|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/g;
    
    let placeholders = [];
    let tempText = text.replace(urlRegex, (match) => {
        placeholders.push(match);
        return `__URL_PH_${placeholders.length - 1}__`;
    });

    tempText = tempText.replace(/[a-ząćęłńóśźżěьъ']+/gi, (word) => {
        const lowWord = word.toLowerCase();
        if (dict[lowWord]) {
            return applyCase(dict[lowWord], getCase(word));
        }
        return word;
    });

    return tempText.replace(/__URL_PH_(\d+)__/g, (match, id) => placeholders[id]);
}

function reorderSmart(text) {
    if (!text) return "";
    const tokens = text.split(/(\s+|[.,!?;:()=+\-%*/]+)/g).filter(t => t !== "" && t !== undefined);
    const result = [];

    for (let i = 0; i < tokens.length; i++) {
        let token = tokens[i];
        let lowToken = token.toLowerCase();

        if (/^[\s.,!?;:()=+\-%*/]+$/.test(token)) {
            result.push(token);
            continue;
        }

        let nextIdx = i + 1;
        while (nextIdx < tokens.length && /^[\s]+$/.test(tokens[nextIdx])) nextIdx++;

        if (nextIdx < tokens.length) {
            let nextToken = tokens[nextIdx];
            let nextLow = nextToken.toLowerCase();

            // Rzeczownik + (Przymiotnik lub Liczebnik)
            if (wordTypes[lowToken] === "noun" && (wordTypes[nextLow] === "adjective" || wordTypes[nextLow] === "numeral")) {
                const firstCase = getCase(token);
                
                // Przymiotnik na przód z wielkością liter pierwotnego pierwszego słowa
                result.push(applyCase(nextToken, firstCase));
                
                // Zachowanie spacji między słowami
                for (let j = i + 1; j < nextIdx; j++) result.push(tokens[j]);
                
                // Rzeczownik na drugie miejsce (małą literą, chyba że pierwotnie był ALL CAPS)
                result.push(firstCase === "upper" ? token.toUpperCase() : token.toLowerCase());
                
                i = nextIdx;
                continue;
            }
        }
        result.push(token);
    }
    return result.join("");
}

async function translate() {
    const input = document.getElementById('userInput');
    const out = document.getElementById('resultOutput');
    if (!input || !out) return;

    const text = input.value;
    const src = document.getElementById('srcLang').value;
    const tgt = document.getElementById('tgtLang').value;

    if (!text.trim()) { out.innerText = ""; return; }

    try {
        let finalResult = "";
        if (src === 'slo' && tgt === 'pl') {
            finalResult = dictReplace(text, sloToPl);
        } else if (src === 'pl' && tgt === 'slo') {
            let translated = dictReplace(text, plToSlo);
            finalResult = reorderSmart(translated);
        } else if (src === 'slo') {
            const bridge = dictReplace(text, sloToPl);
            finalResult = await google(bridge, 'pl', tgt);
        } else if (tgt === 'slo') {
            const bridge = await google(text, src, 'pl');
            let translated = dictReplace(bridge, plToSlo);
            finalResult = reorderSmart(translated);
        } else {
            finalResult = await google(text, src, tgt);
        }
        out.innerText = finalResult;
    } catch (e) { out.innerText = "Error..."; }
}

async function google(text, s, t) {
    try {
        const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=${s}&tl=${t}&dt=t&q=${encodeURIComponent(text)}`;
        const res = await fetch(url);
        const data = await res.json();
        return data[0].map(x => x[0]).join('');
    } catch (e) { return text; }
}

async function loadDictionaries() {
    const status = document.getElementById('dbStatus');
    try {
        const files = ['osnova.json', 'vuzor.json'];
        for (const file of files) {
            const res = await fetch(file);
            if (res.ok) {
                const data = await res.json();
                data.forEach(item => {
                    if (item.polish && item.slovian) {
                        const pl = item.polish.toLowerCase().trim();
                        const slo = item.slovian.toLowerCase().trim();
                        plToSlo[pl] = item.slovian.trim();
                        sloToPl[slo] = item.polish.trim();

                        if (item["type and case"]) {
                            const info = item["type and case"].toLowerCase();
                            if (info.includes("jimenьnik") || info.includes("noun")) wordTypes[slo] = "noun";
                            if (info.includes("priloga") || info.includes("adjective")) wordTypes[slo] = "adjective";
                            if (info.includes("ličьnik") || info.includes("numeral")) wordTypes[slo] = "numeral";
                        }
                    }
                });
            }
        }
        if (status) status.innerText = "Engine Ready.";
    } catch (e) { if (status) status.innerText = "Dict Error."; }
}

async function init() {
    const sysLang = navigator.language.split('-')[0];
    const uiKey = uiTranslations[sysLang] ? sysLang : 'en';
    applyUI(uiKey);
    populateLanguageLists(uiKey);

    const savedSrc = localStorage.getItem('srcLang') || (sysLang === 'pl' ? 'pl' : 'en');
    const savedTgt = localStorage.getItem('tgtLang') || 'slo';

    document.getElementById('srcLang').value = savedSrc;
    document.getElementById('tgtLang').value = savedTgt;

    await loadDictionaries();
    document.getElementById('userInput').addEventListener('input', debounce(() => translate(), 300));
}

function applyUI(lang) {
    const ui = uiTranslations[lang] || uiTranslations.en;
    const ids = ['ui-title', 'ui-label-from', 'ui-label-to', 'ui-paste', 'ui-clear', 'ui-copy'];
    ids.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.innerText = ui[id.replace('ui-', '')] || "";
    });
    const input = document.getElementById('userInput');
    if (input) input.placeholder = ui.placeholder;
}

function populateLanguageLists(uiLang) {
    const srcSelect = document.getElementById('srcLang');
    const tgtSelect = document.getElementById('tgtLang');
    if (!srcSelect || !tgtSelect) return;
    srcSelect.options.length = 0; tgtSelect.options.length = 0;
    languageData.forEach(lang => {
        const name = lang[uiLang] || lang.en;
        srcSelect.add(new Option(name, lang.code));
        tgtSelect.add(new Option(name, lang.code));
    });
}

function swapLanguages() {
    const src = document.getElementById('srcLang');
    const tgt = document.getElementById('tgtLang');
    [src.value, tgt.value] = [tgt.value, src.value];
    localStorage.setItem('srcLang', src.value);
    localStorage.setItem('tgtLang', tgt.value);
    translate();
}

function clearText() {
    document.getElementById('userInput').value = "";
    document.getElementById('resultOutput').innerText = "";
}

function copyText() {
    const text = document.getElementById('resultOutput').innerText;
    navigator.clipboard.writeText(text);
}

async function pasteText() {
    try {
        const text = await navigator.clipboard.readText();
        document.getElementById('userInput').value = text;
        translate();
    } catch(e) { console.log("Clipboard error"); }
}

function debounce(func, wait) {
    let timeout;
    return function() {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, arguments), wait);
    };
}

window.onload = init;
