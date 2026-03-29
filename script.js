/**
 * Logika sortowania słów: numeral -> adjective -> noun
 */
let plToSlo = {}, sloToPl = {};
let dictionaryData = []; 

const weights = { 'numeral': 1, 'adjective': 2, 'noun': 3 };

function orderSlovianPhrase(words) {
    // Sortujemy tylko jeśli mamy przynajmniej jeden znany typ inny niż unknown
    const hasKnownTypes = words.some(w => w.type !== 'unknown');
    if (!hasKnownTypes) return words;

    return [...words].sort((a, b) => {
        const weightA = weights[a.type] || 99;
        const weightB = weights[b.type] || 99;
        return weightA - weightB;
    });
}

function findWordType(word) {
    const low = word.toLowerCase().trim();
    
    // 1. Szukanie bezpośrednie
    let entry = dictionaryData.find(d => d.slovian && d.slovian.toLowerCase() === low);
    
    // 2. Szukanie "rozmyte" (jeśli słowo ma końcówkę gramatyczną)
    if (!entry) {
        entry = dictionaryData.find(d => {
            if (!d.slovian) return false;
            const base = d.slovian.toLowerCase();
            // Sprawdza czy słowo zaczyna się od rdzenia ze słownika (min 3 litery)
            return low.startsWith(base.substring(0, Math.max(3, base.length - 2)));
        });
    }

    if (entry && entry['type and case']) {
        const typePart = entry['type and case'].split(' - ')[0].trim().toLowerCase();
        // Mapowanie nazw na klucze wag
        if (typePart.includes('numeral')) return 'numeral';
        if (typePart.includes('adjective')) return 'adjective';
        if (typePart.includes('noun')) return 'noun';
    }
    return 'unknown';
}

function smartReorder(text) {
    // Rozbijanie na segmenty (zdania/frazy)
    return text.split(/([.!?\n,]+)/).map(segment => {
        if (/^[.!?\n,]+$/.test(segment) || segment.trim() === "") return segment;
        
        // Rozbijamy na słowa zachowując spacje jako oddzielne elementy lub używamy filter
        const tokens = segment.split(/(\s+)/);
        const wordsOnly = [];
        const positions = [];

        // Wyciągamy tylko słowa do posortowania
        tokens.forEach((token, index) => {
            if (token.trim().length > 0) {
                wordsOnly.push({
                    original: token,
                    type: findWordType(token),
                    pos: index
                });
            }
        });

        if (wordsOnly.length < 2) return segment;

        const sortedWords = orderSlovianPhrase(wordsOnly);
        
        // Rekonstrukcja segmentu z nową kolejnością
        let wordIdx = 0;
        return tokens.map((token, index) => {
            if (token.trim().length > 0) {
                return sortedWords[wordIdx++].original;
            }
            return token;
        }).join('');
    }).join('');
}

// --- RESZTA FUNKCJI (translate, google, loadDictionaries itd.) ---

async function translate() {
    const userInput = document.getElementById('userInput');
    const out = document.getElementById('resultOutput');
    if (!userInput) return;
    
    const text = userInput.value.trim();
    const src = document.getElementById('srcLang').value;
    const tgt = document.getElementById('tgtLang').value;
    
    if (!text) { out.innerText = ""; return; }

    try {
        let finalResult = "";
        if (src === 'slo' && tgt === 'pl') {
            finalResult = dictReplace(text, sloToPl);
        } else if (src === 'pl' && tgt === 'slo') {
            let temp = dictReplace(text, plToSlo);
            finalResult = smartReorder(temp);
        } else if (src === 'slo') {
            const bridge = dictReplace(text, sloToPl);
            finalResult = await google(bridge, 'pl', tgt);
        } else if (tgt === 'slo') {
            const bridge = await google(text, src, 'pl');
            // Najpierw zamiana słownikowa, potem reorder
            let temp = dictReplace(bridge, plToSlo);
            finalResult = smartReorder(temp);
        } else {
            finalResult = await google(text, src, tgt);
        }
        out.innerText = finalResult || "";
    } catch (e) { out.innerText = "Error..."; }
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
        if(status) status.innerText = "Engine Ready. v4.1";
    } catch (e) { if(status) status.innerText = "Dict Error."; }
}

// Funkcje pomocnicze UI
async function init() {
    const sysLang = navigator.language.split('-')[0];
    const uiKey = uiTranslations[sysLang] ? sysLang : 'en';
    applyUI(uiKey);
    populateLanguageLists(uiKey);
    
    document.getElementById('srcLang').value = localStorage.getItem('srcLang') || (sysLang === 'pl' ? 'pl' : 'en');
    document.getElementById('tgtLang').value = localStorage.getItem('tgtLang') || 'slo';
    
    await loadDictionaries();
    
    document.getElementById('userInput').addEventListener('input', debounce(() => translate(), 400));
    document.getElementById('srcLang').onchange = (e) => { localStorage.setItem('srcLang', e.target.value); translate(); };
    document.getElementById('tgtLang').onchange = (e) => { localStorage.setItem('tgtLang', e.target.value); translate(); };
}

function applyUI(lang) {
    const ui = uiTranslations[lang] || uiTranslations.en;
    const ids = ['ui-title', 'ui-label-from', 'ui-label-to', 'ui-paste', 'ui-clear', 'ui-copy'];
    ids.forEach(id => {
        const el = document.getElementById(id);
        if(el) el.innerText = ui[id.replace('ui-', '')];
    });
    if(document.getElementById('userInput')) document.getElementById('userInput').placeholder = ui.placeholder;
}

function populateLanguageLists(uiLang) {
    const srcSelect = document.getElementById('srcLang');
    const tgtSelect = document.getElementById('tgtLang');
    if(!srcSelect || !tgtSelect) return;
    languageData.forEach(lang => {
        const name = lang[uiLang] || lang.en;
        srcSelect.add(new Option(name, lang.code));
        tgtSelect.add(new Option(name, lang.code));
    });
}

function swapLanguages() {
    const src = document.getElementById('srcLang');
    const tgt = document.getElementById('tgtLang');
    const temp = src.value;
    src.value = tgt.value;
    tgt.value = temp;
    localStorage.setItem('srcLang', src.value);
    localStorage.setItem('tgtLang', tgt.value);
    translate();
}

function debounce(func, wait) {
    let timeout;
    return function() {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, arguments), wait);
    };
}

// Uruchomienie
window.onload = init;

// Funkcje pomocnicze przycisków
async function pasteText() {
    try {
        const text = await navigator.clipboard.readText();
        document.getElementById('userInput').value = text;
        translate();
    } catch(e) {}
}
function copyText() {
    navigator.clipboard.writeText(document.getElementById('resultOutput').innerText);
}
function clearText() {
    document.getElementById('userInput').value = "";
    document.getElementById('resultOutput').innerText = "";
}
