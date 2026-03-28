let plToSlo = {}, sloToPl = {};

const languageData = [ /* cały array languageData z oryginalnego kodu */ ];
const uiTranslations = { /* cały obiekt uiTranslations z oryginalnego kodu */ };

async function init() {
    const sysLang = navigator.language.split('-')[0];
    const uiKey = uiTranslations[sysLang] ? sysLang : 'en';
   
    applyUI(uiKey);
    populateLanguageLists(uiKey);
   
    let defaultSrc = 'en';
    let defaultTgt = 'slo';
    if(sysLang === 'pl') defaultSrc = 'pl';
   
    const savedSrc = localStorage.getItem('srcLang') || defaultSrc;
    const savedTgt = localStorage.getItem('tgtLang') || defaultTgt;
   
    document.getElementById('srcLang').value = savedSrc;
    document.getElementById('tgtLang').value = savedTgt;
   
    await loadDictionaries();
   
    document.getElementById('userInput').addEventListener('input', debounce(() => translate(), 300));
    document.getElementById('srcLang').onchange = (e) => { localStorage.setItem('srcLang', e.target.value); translate(); };
    document.getElementById('tgtLang').onchange = (e) => { localStorage.setItem('tgtLang', e.target.value); translate(); };
}

// Wklej tutaj resztę funkcji: applyUI, populateLanguageLists, loadDictionaries, translate, google, dictReplace, swapLanguages, pasteText, copyText, clearText, debounce

window.onload = init;
