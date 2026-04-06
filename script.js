let plToSlo = {}, sloToPl = {};
let wordTypes = {};
const languageData = [
    { code: 'slo', slo: 'Slověnьsky', pl: 'Słowiański', en: 'Slovian (Slavic)', de: 'Slawisch', cs: 'Slovanský', sk: 'Slovanský', ru: 'Славянский', fr: 'Slave', es: 'Eslavo', it: 'Slavo', uk: 'Слов\'янська', be: 'Славянская', bg: 'Славянски', hr: 'Slavenski', sr: 'Словенски', 'sr-Latn': 'Slavenski', sl: 'Slovanski', mk: 'Словенски', pt: 'Eslavo', nl: 'Slavisch', da: 'Slavisk', sv: 'Slaviska', no: 'Slavisk', fi: 'Slaavilainen', et: 'Slaavi', lv: 'Slāvu', lt: 'Slavų', el: 'Σλαβική', tr: 'Slavca', hu: 'Szláv', ro: 'Slavă', ja: 'スラヴ語', ko: '슬라브어', "zh-CN": '斯拉夫语', "zh-TW": '斯拉夫語', ar: 'السلافية', hi: 'स्लाविक', id: 'Slavia', vi: 'Tiếng Slav', th: 'ภาษาสลาวิก', he: 'סלאבית', az: 'Slavyan', ka: 'სლავური', hy: 'Սլավոնական', af: 'Slawies', sq: 'Sllave', am: 'ስላቪክ', bn: 'স্লাভিক', ms: 'Slavik', zu: 'IsiSlavic' },
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
    { code: 'bn', pl: 'Bengalski', en: 'Bengali', slo: 'Bengalьsky', de: 'Bengalisch' },
    { code: 'be', pl: 'Białoruski', en: 'Belarusian', slo: 'Bělorusьsky', de: 'Weißrussisch' },
    { code: 'bg', pl: 'Bułgarski', en: 'Bulgarian', slo: "Bulgar'ьsky", de: 'Bulgarisch' },
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
    { code: 'ga', pl: 'Irlandzki', en: 'Irish', slo: 'Irьski', de: 'Irisch' },
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
    { code: 'vi', pl: 'Wietnamski', en: 'Vietnamese', slo: 'Větnamьsky', de: 'Vietnamesisch' }
];
const uiTranslations = {
    slo: { title: "Slovo Perkladačь", from: "Jiz ęzyka:", to: "Na ęzyk:", paste: "Vyloži", clear: "Terbi", copy: "Poveli", placeholder: "Piši tu..." },
    pl: { title: "Slovo Tłumacz", from: "Z języka:", to: "Na język:", paste: "Wklej", clear: "Usuń", copy: "Kopiuj", placeholder: "Wpisz tekst..." },
    en: { title: "Slovo Translator", from: "From language:", to: "To language:", paste: "Paste", clear: "Clear", copy: "Copy", placeholder: "Type here..." },
    de: { title: "Slovo Übersetzer", from: "Von:", to: "Nach:", paste: "Einfügen", clear: "Löschen", copy: "Kopieren", placeholder: "Text eingeben..." },
    fr: { title: "Traducteur Slovo", from: "De :", to: "Vers :", paste: "Coller", clear: "Effacer", copy: "Copier", placeholder: "Entrez le texte..." },
    es: { title: "Traductor Slovo", from: "De:", to: "A:", paste: "Pegar", clear: "Borrar", copy: "Copier", placeholder: "Escribe texto..." },
    it: { title: "Traduttore Slovo", from: "Da:", to: "A:", paste: "Incolla", clear: "Cancella", copy: "Copia", placeholder: "Inserisci testo..." },
    pt: { title: "Tradutor Slovo", from: "De:", to: "Para:", paste: "Colar", clear: "Limpar", copy: "Copiar", placeholder: "Digite o texto..." },
    nl: { title: "Slovo Vertaler", from: "Van:", to: "Naar:", paste: "Plakken", clear: "Wissen", copy: "Kopiëren", placeholder: "Voer tekst in..." },
    sv: { title: "Slovo Översättare", from: "Från:", to: "Till:", paste: "Klistra in", clear: "Rensa", copy: "Kopiera", placeholder: "Skriv text..." },
    no: { title: "Slovo Oversetter", from: "Fra:", to: "Til:", paste: "Lim inn", clear: "Fjern", copy: "Kopier", placeholder: "Skriv tekst..." },
    da: { title: "Slovo Oversætter", from: "Fra:", to: "Til:", paste: "Indsæt", clear: "Ryd", copy: "Kopiér", placeholder: "Indtast tekst..." },
    fi: { title: "Slovo Kääntäjä", from: "Lähde:", to: "Kohde:", paste: "Liitä", clear: "Tyhjennä", copy: "Kopioi", placeholder: "Kirjoita teksti..." },
    ru: { title: "Slovo Переводчик", from: "С языка:", to: "На язык:", paste: "Вставить", clear: "Очистить", copy: "Копировать", placeholder: "Введите текст..." },
    uk: { title: "Slovo Перекладач", from: "З мови:", to: "На мову:", paste: "Вставити", clear: "Очистити", copy: "Копіювати", placeholder: "Введіть текст..." },
    cs: { title: "Slovo Překladač", from: "Z jazyka:", to: "Do jazyka:", paste: "Vložit", clear: "Vymazat", copy: "Kopírovat", placeholder: "Zadejte text..." },
    sk: { title: "Slovo Prekladač", from: "Z jazyka:", to: "Do jazyka:", paste: "Vložiť", clear: "Vymazať", copy: "Kopírovat", placeholder: "Zadajte text..." },
    sl: { title: "Slovo Prevajalnik", from: "Iz:", to: "V:", paste: "Prilepi", clear: "Počisti", copy: "Kopiraj", placeholder: "Vnesi besedilo..." },
    hr: { title: "Slovo Prevoditelj", from: "Iz:", to: "U:", paste: "Zalijepi", clear: "Obriši", copy: "Kopiraj", placeholder: "Unesi tekst..." },
    sr: { title: "Slovo Преводилац", from: "Са језика:", to: "На језик:", paste: "Налепи", clear: "Обриши", copy: "Копирај", placeholder: "Унеси текст..." },
    'sr-Latn': { title: "Slovo Prevodilac", from: "Sa jezika:", to: "Na jezik:", paste: "Nalepi", clear: "Obriši", copy: "Kopiraj", placeholder: "Unesi tekst..." },
    bg: { title: "Slovo Преводач", from: "От:", to: "На:", paste: "Постави", clear: "Изчисти", copy: "Копирай", placeholder: "Въведи текст..." },
    tr: { title: "Slovo Çevirici", from: "Dilden:", to: "Dile:", paste: "Yapıştır", clear: "Temizle", copy: "Kopyala", placeholder: "Metin gir..." },
    el: { title: "Slovo Μεταφραστής", from: "Από:", to: "Προς:", paste: "Επικόλληση", clear: "Καθαρισμός", copy: "Αντιγραφή", placeholder: "Εισάγετε κείμενο..." },
    ro: { title: "Traducător Slovo", from: "Din:", to: "În:", paste: "Lipește", clear: "Șterge", copy: "Copiază", placeholder: "Introdu text..." },
    hu: { title: "Slovo Fordító", from: "Erről:", to: "Erre:", paste: "Beillesztés", clear: "Törlés", copy: "Másolás", placeholder: "Írj szöveget..." },
    zh: { title: "Slovo 翻译器", from: "从:", to: "到:", paste: "粘贴", clear: "清除", copy: "复制", placeholder: "输入文本..." },
    ja: { title: "Slovo 翻訳", from: "元の言語:", to: "翻訳先:", paste: "貼り付け", clear: "クリア", copy: "コピー", placeholder: "テキストを入力..." },
    ko: { title: "Slovo 번역기", from: "출발:", to: "도착:", paste: "붙여넣기", clear: "지우기", copy: "복사", placeholder: "텍스트 입력..." },
    ar: { title: "مترجم Slovo", from: "من:", to: "إلى:", paste: "لصق", clear: "مسح", copy: "نسخ", placeholder: "أدخل النص..." }
};

// Funkcja dopasowująca wielkość liter (Case Sensitivity)
function matchCase(original, target) {
    if (original === original.toUpperCase()) return target.toUpperCase();
    if (original[0] === original[0].toUpperCase()) return target.charAt(0).toUpperCase() + target.slice(1).toLowerCase();
    return target.toLowerCase();
}

// Funkcja naprawiająca szyk: Rzeczownik + Przymiotnik -> Przymiotnik + Rzeczownik
function fixSlovianWordOrder(text) {
    // Rozbijamy na słowa, spacje i interpunkcję
    let tokens = text.split(/([a-ząćęłńóśźżěьъ]+|\s+|[.,!?;:]+)/gi).filter(Boolean);
    
    for (let i = 0; i < tokens.length - 2; i++) {
        let current = tokens[i];
        let next = tokens[i + 2];
        
        if (!next) continue;

        let cleanA = current.toLowerCase().replace(/[.,!?;:]/g, "").trim();
        let cleanB = next.toLowerCase().replace(/[.,!?;:]/g, "").trim();

        if (wordTypes[cleanA] === 'noun' && (wordTypes[cleanB] === 'adjective' || wordTypes[cleanB] === 'numeral')) {
            let punctA = current.match(/[.,!?;:]+$/) || "";
            let punctB = next.match(/[.,!?;:]+$/) || "";

            // Zamiana
            let newFirst = matchCase(current, cleanB);
            let newSecond = matchCase(next, cleanA);

            tokens[i] = newFirst; 
            tokens[i + 2] = newSecond + punctB + punctA; // Przenosimy interpunkcję na koniec
            i += 2;
        }
    }
    return tokens.join('');
}

function dictReplace(text, dict) {
    return text.replace(/[a-ząćęłńóśźżěьъ]+/gi, (m) => {
        const low = m.toLowerCase();
        if (dict[low]) {
            const r = dict[low];
            if (m === m.toUpperCase()) return r.toUpperCase();
            if (m[0] === m[0].toUpperCase()) return r.charAt(0).toUpperCase() + r.slice(1);
            return r;
        }
        return m;
    });
}

async function google(text, s, t) {
    try {
        const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=${s}&tl=${t}&dt=t&q=${encodeURIComponent(text)}`;
        const res = await fetch(url);
        const data = await res.json();
        return data[0].map(x => x[0]).join('');
    } catch (e) { return text; }
}

async function translate() {
    const text = document.getElementById('userInput').value.trim();
    const src = document.getElementById('srcLang').value;
    const tgt = document.getElementById('tgtLang').value;
    const out = document.getElementById('resultOutput');
    
    if (!text) { out.innerText = ""; return; }
    
    try {
        let res = "";
        if (src === 'pl' && tgt === 'slo') {
            res = fixSlovianWordOrder(dictReplace(text, plToSlo));
        } else if (tgt === 'slo') {
            const bridge = await google(text, src, 'pl');
            res = fixSlovianWordOrder(dictReplace(bridge, plToSlo));
        } else if (src === 'slo') {
            const bridge = dictReplace(text, sloToPl);
            res = await google(bridge, 'pl', tgt);
        } else {
            res = await google(text, src, tgt);
        }
        out.innerText = res;
    } catch (e) { out.innerText = "..."; }
}

async function loadDictionaries() {
    try {
        const files = ['osnova.json', 'vuzor.json'];
        for (const file of files) {
            const res = await fetch(file);
            if (res.ok) {
                const data = await res.json();
                data.forEach(item => {
                    if (item.polish && item.slovian) {
                        let s = item.slovian.toLowerCase().trim();
                        let p = item.polish.toLowerCase().trim();
                        plToSlo[p] = item.slovian.trim();
                        sloToPl[s] = item.polish.trim();
                        
                        let info = (item['type and case'] || "").toLowerCase();
                        if (info.includes('noun') || info.includes('jimenovnik')) wordTypes[s] = 'noun';
                        else if (info.includes('adjective') || info.includes('pridavnik')) wordTypes[s] = 'adjective';
                        else if (info.includes('numeral') || info.includes('ličebnik')) wordTypes[s] = 'numeral';
                    }
                });
            }
        }
        document.getElementById('dbStatus').innerText = "Engine Ready.";
    } catch (e) { document.getElementById('dbStatus').innerText = "Load Error."; }
}

function applyUI(langKey) {
    const ui = uiTranslations[langKey] || uiTranslations.en;
    document.getElementById('ui-title').innerText = ui.title;
    document.getElementById('ui-label-from').innerText = ui.from;
    document.getElementById('ui-label-to').innerText = ui.to;
    document.getElementById('ui-paste').innerText = ui.paste;
    document.getElementById('ui-clear').innerText = ui.clear;
    document.getElementById('ui-copy').innerText = ui.copy;
    document.getElementById('userInput').placeholder = ui.placeholder;
}

function populateLanguageLists(uiLang) {
    const srcS = document.getElementById('srcLang');
    const tgtS = document.getElementById('tgtLang');
    srcS.innerHTML = ""; tgtS.innerHTML = "";
    languageData.forEach(l => {
        const name = l[uiLang] || l.en;
        srcS.add(new Option(name, l.code));
        tgtS.add(new Option(name, l.code));
    });
}

// Funkcje przycisków
function clearText() {
    document.getElementById('userInput').value = "";
    document.getElementById('resultOutput').innerText = "";
}

async function pasteText() {
    const text = await navigator.clipboard.readText();
    document.getElementById('userInput').value = text;
    translate();
}

function copyText() {
    navigator.clipboard.writeText(document.getElementById('resultOutput').innerText);
}

const debounce = (fn, ms) => {
    let timeoutId;
    return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn.apply(null, args), ms);
    };
};

async function init() {
    // Wykrywanie języka urządzenia
    const browserLang = navigator.language.split('-')[0];
    const uiKey = uiTranslations[browserLang] ? browserLang : 'en';
    
    applyUI(uiKey);
    populateLanguageLists(uiKey);

    // Ustawienie domyślnych języków
    document.getElementById('srcLang').value = localStorage.getItem('srcLang') || (browserLang === 'pl' ? 'pl' : 'en');
    document.getElementById('tgtLang').value = localStorage.getItem('tgtLang') || 'slo';

    await loadDictionaries();

    // Event Listeners
    document.getElementById('userInput').addEventListener('input', debounce(translate, 300));
    document.getElementById('srcLang').onchange = (e) => { localStorage.setItem('srcLang', e.target.value); translate(); };
    document.getElementById('tgtLang').onchange = (e) => { localStorage.setItem('tgtLang', e.target.value); translate(); };
    
    // Podpięcie przycisków (ważne!)
    document.getElementById('ui-clear').onclick = clearText;
    document.getElementById('ui-paste').onclick = pasteText;
    document.getElementById('ui-copy').onclick = copyText;
}

window.onload = init;
