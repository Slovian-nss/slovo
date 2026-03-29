let plToSlo = {}, sloToPl = {};
let wordTypes = {};
let wordCases = {};

// DODANE: Obiekt z tłumaczeniami interfejsu (bez tego kod wyrzuca błąd)
const uiTranslations = {
    pl: {
        title: "Tłumacz Międzysłowiański",
        from: "Z języka:",
        to: "Na język:",
        paste: "Wklej",
        clear: "Wyczyść",
        copy: "Kopiuj",
        placeholder: "Wpisz tekst..."
    },
    en: {
        title: "Interslavic Translator",
        from: "From:",
        to: "To:",
        paste: "Paste",
        clear: "Clear",
        copy: "Copy",
        placeholder: "Type something..."
    }
};

const languageData = [
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
    { code: 'ja', pl: 'Japoński', en: 'Japanese', slo: 'Japonьsky', de: 'Japanisch' },
    { code: 'tr', pl: 'Turecki', en: 'Turkish', slo: 'Turečьsky', de: 'Türkisch' }
    // ... reszta Twoich języków ...
];

function reorderSmart(text) {
    if (!text) return "";
    const words = text.split(/\s+/);
    const result = [];
    let i = 0;
    while (i < words.length) {
        let group = { numeral: null, modifiers: [], adjectives: [], noun: null };
        
        // Naprawa: Bezpieczne sprawdzanie słowa
        let w = words[i] ? words[i].toLowerCase() : "";

        while (i < words.length && ["bardzo", "velmi"].includes(words[i].toLowerCase())) {
            group.modifiers.push(words[i]);
            i++;
        }

        if (i < words.length && wordTypes[words[i].toLowerCase()] === "numeral") {
            group.numeral = words[i++];
        }

        while (i < words.length && wordTypes[words[i].toLowerCase()] === "adjective") {
            group.adjectives.push(words[i++]);
        }

        if (i < words.length && wordTypes[words[i].toLowerCase()] === "noun") {
            group.noun = words[i++];
        }

        if (group.noun) {
            if (group.numeral) result.push(group.numeral);
            if (group.modifiers.length) result.push(...group.modifiers);
            if (group.adjectives.length) result.push(...group.adjectives);
            result.push(group.noun);
        } else {
            if (words[i]) result.push(words[i]);
            i++; // Kluczowe: zapobiega nieskończonej pętli
        }
    }
    return result.join(" ");
}

function dictReplace(text, dict) {
    if (!text) return "";
    // Rozszerzony regex o znaki słowiańskie
    return text.replace(/[a-ząćęłńóśźżěьъ]+|([0-9]+)/gi, (m) => {
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
    } catch (e) { 
        console.error("Google API error:", e);
        return text; 
    }
}

async function translate() {
    const inputEl = document.getElementById('userInput');
    const outEl = document.getElementById('resultOutput');
    if (!inputEl || !outEl) return;

    const text = inputEl.value.trim();
    const src = document.getElementById('srcLang').value;
    const tgt = document.getElementById('tgtLang').value;

    if (!text) { outEl.innerText = ""; return; }

    try {
        let finalResult = "";
        if (src === 'slo' && tgt === 'pl') {
            finalResult = dictReplace(text, sloToPl);
        } else if (src === 'pl' && tgt === 'slo') {
            let temp = dictReplace(text, plToSlo);
            finalResult = reorderSmart(temp);
        } else if (src === 'slo') {
            const bridge = dictReplace(text, sloToPl);
            finalResult = await google(bridge, 'pl', tgt);
        } else if (tgt === 'slo') {
            const bridge = await google(text, src, 'pl');
            let temp = dictReplace(bridge, plToSlo);
            finalResult = reorderSmart(temp);
        } else {
            finalResult = await google(text, src, tgt);
        }
        outEl.innerText = finalResult || "";
    } catch (e) {
        outEl.innerText = "Błąd tłumaczenia...";
    }
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
                    // Dopasowanie do Twoich kluczy w pliku JSON
                    const plWord = item.polish || item.pl;
                    const sloWord = item.slovian || item.slo;

                    if (plWord && sloWord) {
                        const pl = plWord.toLowerCase().trim();
                        const slo = sloWord.toLowerCase().trim();
                        plToSlo[pl] = sloWord.trim();
                        sloToPl[slo] = plWord.trim();

                        const typeInfo = item["type and case"] || "";
                        const info = typeInfo.toLowerCase();
                        if (info.includes("noun")) wordTypes[slo] = "noun";
                        if (info.includes("adjective")) wordTypes[slo] = "adjective";
                        if (info.includes("numeral")) wordTypes[slo] = "numeral";
                        wordCases[slo] = info;
                    }
                });
            }
        }
        if (status) status.innerText = "Silnik gotowy.";
    } catch (e) {
        if (status) status.innerText = "Błąd słowników.";
    }
}

function applyUI(lang) {
    const ui = uiTranslations[lang] || uiTranslations.en;
    // Bezpieczne sprawdzanie czy elementy istnieją w HTML
    const elements = {
        'ui-title': 'title',
        'ui-label-from': 'from',
        'ui-label-to': 'to',
        'ui-paste': 'paste',
        'ui-clear': 'clear',
        'ui-copy': 'copy'
    };

    for (let [id, key] of Object.entries(elements)) {
        const el = document.getElementById(id);
        if (el) el.innerText = ui[key];
    }
    
    const input = document.getElementById('userInput');
    if (input) input.placeholder = ui.placeholder;
}

function populateLanguageLists(uiLang) {
    const srcSelect = document.getElementById('srcLang');
    const tgtSelect = document.getElementById('tgtLang');
    if (!srcSelect || !tgtSelect) return;

    srcSelect.options.length = 0;
    tgtSelect.options.length = 0;
    
    languageData.forEach(lang => {
        const name = lang[uiLang] || lang.en;
        srcSelect.add(new Option(name, lang.code));
        tgtSelect.add(new Option(name, lang.code));
    });

    // Domyślne wartości
    srcSelect.value = 'pl';
    tgtSelect.value = 'slo';
}

function debounce(func, wait) {
    let timeout;
    return function() {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, arguments), wait);
    };
}

async function init() {
    const sysLang = navigator.language.split('-')[0];
    const uiKey = uiTranslations[sysLang] ? sysLang : 'en';
    
    applyUI(uiKey);
    populateLanguageLists(uiKey);
    await loadDictionaries();
    
    const input = document.getElementById('userInput');
    if (input) {
        input.addEventListener('input', debounce(() => translate(), 300));
    }
}

window.onload = init;
