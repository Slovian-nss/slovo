let plToSlo = {}, sloToPl = {};
let dictionaryData = [];

const languageData = [
    { code: 'slo', pl: 'Słowiański', en: 'Slovian (Slavic)', slo: 'Slověnьsky', de: 'Slawisch' },
    { code: 'en', pl: 'Angielski', en: 'English', slo: "Angol'ьsky", de: 'Englisch' },
    { code: 'pl', pl: 'Polski', en: 'Polish', slo: "Pol'ьsky", de: 'Polnisch' },
    { code: 'de', pl: 'Niemiecki', en: 'German', slo: 'Nemьčьsky', de: 'Deutsch' },
    { code: 'cs', pl: 'Czeski', en: 'Czech', slo: 'Češьsky', de: 'Tschechisch' },
    { code: 'sk', pl: 'Słowacki', en: 'Slovak', slo: 'Slovačьsky', de: 'Slowakisch' },
    { code: 'ru', pl: 'Rosyjski', en: 'Russian', slo: 'Rusьsky', de: 'Russisch' },
    { code: 'zh-CN', pl: 'Chiński (uproszczony)', en: 'Chinese (Simplified)', slo: 'Kitajьsky (Uproščeny)', de: 'Chinesisch' }
];

const uiTranslations = {
    slo: { title: "Slovo Perkladačь", from: "Jiz ęzyka:", to: "Na ęzyk:", paste: "Vyloži", clear: "Terbi", copy: "Poveli", placeholder: "Piši tu..." },
    pl: { title: "Slovo Tłumacz", from: "Z języka:", to: "Na język:", paste: "Wklej", clear: "Usuń", copy: "Kopiuj", placeholder: "Wpisz tekst..." },
    en: { title: "Slovo Translator", from: "From language:", to: "To language:", paste: "Paste", clear: "Clear", copy: "Copy", placeholder: "Type here..." },
    de: { title: "Slovo Übersetzer", from: "Von:", to: "Nach:", paste: "Einfügen", clear: "Löschen", copy: "Kopieren", placeholder: "Text eingeben..." }
};

const weights = { 'numeral': 1, 'adjective': 2, 'noun': 3 };

function findType(word) {
    const clean = word.toLowerCase().replace(/[.!?,\s]/g, '');
    if (!clean) return 99;
    const entry = dictionaryData.find(d => d.slovian && d.slovian.toLowerCase() === clean);
    if (entry && entry['type and case']) {
        const t = entry['type and case'].toLowerCase();
        if (t.includes('numeral')) return 1;
        if (t.includes('adjective')) return 2;
        if (t.includes('noun')) return 3;
    }
    return 99;
}

function smartReorder(text) {
    return text.split(/([.!?\n]+)/).map(segment => {
        if (/^[.!?\n]+$/.test(segment)) return segment;

        const tokens = segment.split(/(\s+)/);
        let processedTokens = tokens.map(t => ({
            text: t,
            isWord: /[a-ząćęłńóśźżěьъǫ\u0300-\u036f]+/i.test(t),
            weight: /[a-ząćęłńóśźżěьъǫ\u0300-\u036f]+/i.test(t) ? findType(t) : 100
        }));

        // Grupowanie sąsiadujących słów o wagach 1-3 (num/adj/noun)
        let result = [];
        for (let i = 0; i < processedTokens.length; i++) {
            if (processedTokens[i].weight <= 3) {
                let group = [];
                while (i < processedTokens.length && (processedTokens[i].weight <= 3 || processedTokens[i].text.trim() === "")) {
                    if (processedTokens[i].isWord) group.push(processedTokens[i]);
                    i++;
                }
                // Sortuj słowa wewnątrz grupy
                group.sort((a, b) => a.weight - b.weight);
                group.forEach((item, idx) => {
                    result.push(item.text);
                    if (idx < group.length - 1) result.push(" ");
                });
                i--; // cofnij o jeden, bo pętla for doda inkrementację
            } else {
                result.push(processedTokens[i].text);
            }
        }
        return result.join('');
    }).join('');
}

function dictReplace(text, dict) {
    return text.replace(/[a-ząćęłńóśźżěьъǫ\u0300-\u036f'‘’]+/gi, (m) => {
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

async function translate() {
    const input = document.getElementById('userInput');
    const out = document.getElementById('resultOutput');
    if (!input || !out) return;

    const text = input.value.trim();
    const src = document.getElementById('srcLang').value;
    const tgt = document.getElementById('tgtLang').value;

    if (!text) { out.innerText = ""; return; }

    try {
        let res = "";
        if (src === 'pl' && tgt === 'slo') {
            res = smartReorder(dictReplace(text, plToSlo));
        } else if (src === 'slo' && tgt === 'pl') {
            res = dictReplace(text, sloToPl);
        } else if (tgt === 'slo') {
            const bridge = await google(text, src, 'pl');
            res = smartReorder(dictReplace(bridge, plToSlo));
        } else if (src === 'slo') {
            const bridge = dictReplace(text, sloToPl);
            res = await google(bridge, 'pl', tgt);
        } else {
            res = await google(text, src, tgt);
        }
        out.innerText = res;
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
                dictionaryData = [...dictionaryData, ...data];
                data.forEach(item => {
                    if (item.polish && item.slovian) {
                        plToSlo[item.polish.toLowerCase().trim()] = item.slovian.trim();
                        sloToPl[item.slovian.toLowerCase().trim()] = item.polish.trim();
                    }
                });
            }
        }
        if(status) status.innerText = "Engine Ready.";
    } catch (e) { if(status) status.innerText = "Dict Error."; }
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
    
    // UI Setup
    const srcSelect = document.getElementById('srcLang');
    const tgtSelect = document.getElementById('tgtLang');
    if(srcSelect && tgtSelect) {
        languageData.forEach(lang => {
            const name = lang[uiKey] || lang.en;
            srcSelect.add(new Option(name, lang.code));
            tgtSelect.add(new Option(name, lang.code));
        });
    }

    applyUI(uiKey);
    await loadDictionaries();

    const input = document.getElementById('userInput');
    if(input) input.addEventListener('input', debounce(translate, 400));
}

function applyUI(lang) {
    const ui = uiTranslations[lang] || uiTranslations.en;
    const ids = ['ui-title', 'ui-label-from', 'ui-label-to', 'ui-paste', 'ui-clear', 'ui-copy'];
    ids.forEach(id => {
        const el = document.getElementById(id);
        if(el) el.innerText = ui[id.replace('ui-', '')];
    });
}

function swapLanguages() {
    const src = document.getElementById('srcLang');
    const tgt = document.getElementById('tgtLang');
    const tmp = src.value;
    src.value = tgt.value;
    tgt.value = tmp;
    translate();
}

function clearText() {
    document.getElementById('userInput').value = "";
    document.getElementById('resultOutput').innerText = "";
}

function copyText() {
    navigator.clipboard.writeText(document.getElementById('resultOutput').innerText);
}

window.onload = init;
