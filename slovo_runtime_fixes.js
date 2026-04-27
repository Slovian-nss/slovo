/* slovo_runtime_fixes.js
 * Runtime fixes + dynamic noun inflection layer for Slovo Translator.
 *
 * Co robi:
 * 1) uruchamia tłumaczenie po wklejeniu tekstu;
 * 2) wyłącza sugestie korekty przeglądarki typu: grodach -> grozach;
 * 3) jeżeli w JSON-ach nie ma gotowej formy fleksyjnej, próbuje zbudować ją
 *    z hasła podstawowego i wzoru rzeczownika, zwłaszcza dla miejscownika.
 */
(function () {
    "use strict";

    const INPUT_ID = "userInput";
    const OUTPUT_ID = "resultOutput";
    const SRC_ID = "srcLang";
    const TGT_ID = "tgtLang";
    const SUGGESTION_ID = "suggestionBox";

    const TOKEN_RE = /([\p{L}\p{M}0-9'’]+|\s+|[^\s\p{L}\p{M}0-9'’]+)/gu;
    const WORD_RE = /^[\p{L}\p{M}0-9'’]+$/u;
    const LOCATIVE_PREPOSITIONS_PL = new Set(["w", "we", "na", "po", "przy", "o"]);
    const PREP_PL_TO_SLO = new Map([
        ["w", "vu"],
        ["we", "vu"],
        ["na", "na"],
        ["po", "po"],
        ["przy", "pri"],
        ["o", "ob"]
    ]);

    const DATA_FILES = ["vuzor.json", "osnova.json"];

    const INFLECT = {
        loaded: false,
        loading: null,
        exactForms: new Map(),
        generatedForms: new Map()
    };

    let nativeRunLock = false;
    let patchTimer = null;

    function $(id) {
        return document.getElementById(id);
    }

    function normalizeKey(value) {
        return String(value || "")
            .normalize("NFC")
            .replace(/[’]/g, "'")
            .replace(/\s+/g, " ")
            .trim()
            .toLocaleLowerCase("pl");
    }

    function foldPolish(value) {
        return normalizeKey(value)
            .replace(/[ąćęłńóśźż]/g, function (ch) {
                return ({ ą: "a", ć: "c", ę: "e", ł: "l", ń: "n", ó: "o", ś: "s", ź: "z", ż: "z" })[ch] || ch;
            });
    }

    function isWord(token) {
        return WORD_RE.test(token || "") && /[\p{L}\p{M}0-9]/u.test(token || "");
    }

    function isSpace(token) {
        return /^\s+$/.test(token || "");
    }

    function tokenize(text) {
        return String(text || "").match(TOKEN_RE) || [];
    }

    function applyCaseLike(source, target) {
        const src = String(source || "");
        const out = String(target || "");
        if (!out) return out;
        if (src.length > 1 && src === src.toLocaleUpperCase("pl")) return out.toLocaleUpperCase("pl");
        if (src[0] && src[0] === src[0].toLocaleUpperCase("pl") && src[0] !== src[0].toLocaleLowerCase("pl")) {
            return out.charAt(0).toLocaleUpperCase("pl") + out.slice(1);
        }
        return out;
    }

    function fixSpacing(text) {
        return String(text || "")
            .replace(/\s+([,.;:!?%])/g, "$1")
            .replace(/([([{„«])\s+/g, "$1")
            .replace(/\s+([)\]}”»])/g, "$1")
            .replace(/\s+/g, " ")
            .trim();
    }

    function parseMeta(typeCase) {
        const raw = String(typeCase || "");
        const info = normalizeKey(raw);
        const meta = {
            raw,
            wordClass: "unknown",
            grammaticalCase: null,
            number: null,
            gender: null,
            animacy: null,
            lemma: null
        };

        const lemmaMatch = raw.match(/jimenьnik\s*:\s*"([^"]+)"/i);
        if (lemmaMatch && lemmaMatch[1]) meta.lemma = normalizeKey(lemmaMatch[1]);

        if (info.includes("noun") || info.includes("jimenьnik") || info.includes("imenьnik") || info.includes("rzeczownik")) {
            meta.wordClass = "noun";
        }
        if (info.includes("adjective") || info.includes("pridav") || info.includes("przymiotnik")) {
            meta.wordClass = "adjective";
        }
        if (info.includes("verb") || info.includes("glagol") || info.includes("czasownik")) {
            meta.wordClass = "verb";
        }

        if (info.includes("nominative") || info.includes("jimenovьnik") || info.includes("jimeniteljьnik")) meta.grammaticalCase = "nominative";
        else if (info.includes("accusative") || info.includes("vinьnik") || info.includes("viniteljьnik")) meta.grammaticalCase = "accusative";
        else if (info.includes("genitive") || info.includes("rodilьnik") || info.includes("roditeljьnik")) meta.grammaticalCase = "genitive";
        else if (info.includes("locative") || info.includes("městьnik")) meta.grammaticalCase = "locative";
        else if (info.includes("dative") || info.includes("měrьnik")) meta.grammaticalCase = "dative";
        else if (info.includes("instrumental") || info.includes("orǫdьnik") || info.includes("tvoriteljьnik")) meta.grammaticalCase = "instrumental";
        else if (info.includes("vocative") || info.includes("zovanьnik") || info.includes("zovateljьnik")) meta.grammaticalCase = "vocative";

        if (info.includes("singular") || info.includes("poedinьna")) meta.number = "singular";
        else if (info.includes("plural") || info.includes("munoga") || info.includes("munga")) meta.number = "plural";

        if (info.includes("masculine") || info.includes("mǫž") || info.includes("meski") || info.includes("męski")) meta.gender = "masculine";
        else if (info.includes("feminine") || info.includes("žen") || info.includes("zenski") || info.includes("żeński")) meta.gender = "feminine";
        else if (info.includes("neuter") || info.includes("nijak")) meta.gender = "neuter";

        return meta;
    }

    function addIndex(map, key, entry) {
        const folded = foldPolish(key);
        if (!folded) return;
        const old = map.get(folded);
        if (!old || (entry.priority || 0) > (old.priority || 0)) map.set(folded, entry);
    }

    function addGeneratedForms(polishLemma, slovianLemma, meta, priority) {
        const pl = normalizeKey(polishLemma);
        const slo = String(slovianLemma || "").trim();
        if (!pl || !slo || !meta || meta.wordClass !== "noun") return;

        const baseEntry = { polishLemma: pl, slovianLemma: slo, meta, priority: priority || 0 };
        addIndex(INFLECT.generatedForms, pl, baseEntry);

        for (const form of generatePolishLocativeForms(pl)) {
            addIndex(INFLECT.generatedForms, form.form, {
                polishLemma: pl,
                slovianLemma: slo,
                meta,
                grammaticalCase: "locative",
                number: form.number,
                priority: (priority || 0) + form.priority
            });
        }
    }

    function generatePolishLocativeForms(lemma) {
        const forms = [];
        const add = (form, number, priority) => {
            if (form) forms.push({ form, number, priority: priority || 0 });
        };

        const pl = normalizeKey(lemma);
        const folded = foldPolish(pl);

        // Rzeczowniki typu gród/ogród: gród -> grodzie/grodach, ogród -> ogrodzie/ogrodach.
        if (pl.endsWith("ód")) {
            const stem = pl.slice(0, -2) + "od";
            add(stem + "zie", "singular", 80);
            add(stem + "ach", "plural", 90);
        }

        // miasto -> mieście/miastach; ciasto -> cieście/ciastach itd. Wystarcza dla obecnego wzorca.
        if (pl.endsWith("asto")) {
            const stem = pl.slice(0, -4);
            add(stem + "eście", "singular", 85);
            add(stem + "escie", "singular", 80);
            add(pl.slice(0, -1) + "ach", "plural", 90);
        }

        if (pl.endsWith("o")) {
            const stem = pl.slice(0, -1);
            add(stem + "ie", "singular", 50);
            add(stem + "u", "singular", 35);
            add(stem + "ach", "plural", 75);
        } else if (pl.endsWith("e")) {
            const stem = pl.slice(0, -1);
            add(stem + "u", "singular", 35);
            add(stem + "ach", "plural", 75);
        } else if (pl.endsWith("a")) {
            const stem = pl.slice(0, -1);
            add(stem + "ie", "singular", 45);
            add(stem + "y", "singular", 35);
            add(stem + "i", "singular", 35);
            add(stem + "ach", "plural", 75);
        } else if (pl) {
            add(pl + "ie", "singular", 30);
            add(pl + "u", "singular", 25);
            add(folded + "ie", "singular", 20);
            add(folded + "u", "singular", 20);
            add(folded + "ach", "plural", 70);
            add(pl + "ach", "plural", 65);
        }

        return forms;
    }

    function inferGenderFromSlovianLemma(lemma, oldGender) {
        if (oldGender) return oldGender;
        const w = String(lemma || "");
        if (/a$/.test(w)) return "feminine";
        if (/(o|e|ę|ьje|je|stvo)$/.test(w)) return "neuter";
        return "masculine";
    }

    function getStemBeforeFinal(word, finalPattern) {
        return String(word || "").replace(finalPattern, "");
    }

    function inflectSlovianNoun(lemma, meta, grammaticalCase, number) {
        const w = String(lemma || "").trim();
        if (!w || grammaticalCase !== "locative") return w;

        const gender = inferGenderFromSlovianLemma(w, meta && meta.gender);
        const plural = number === "plural";

        if (plural) {
            // Reguła projektu: miękki jer -ь -> -ih; męskie/nijakie -> -ěh; pozostałe -> -ah.
            if (/ь$/.test(w)) return w.slice(0, -1) + "ih";

            if (gender === "masculine" || gender === "neuter") {
                if (/ьje$/.test(w)) return w.slice(0, -1) + "ih";      // bytьje -> bytьjih
                if (/je$/.test(w)) return w.slice(0, -1) + "ih";       // polěsьje -> polěsьjih
                if (/stvo$/.test(w)) return w.slice(0, -1) + "ěh";     // -stvo -> -stvěh
                if (/o$/.test(w)) return w.slice(0, -1) + "ěh";        // dobro -> dobrěh
                if (/e$/.test(w)) return w.slice(0, -1) + "ih";
                return w + "ěh";                                      // gord -> gorděh
            }

            if (/ja$/.test(w)) return w.slice(0, -1) + "ah";           // prodadja -> prodadjah
            if (/a$/.test(w)) return w.slice(0, -1) + "ah";            // okolica -> okolicah
            return w + "ah";
        }

        // Locative singular.
        if (/ь$/.test(w)) return w.slice(0, -1) + "i";                 // mǫdrostь -> mǫdrosti
        if (/ьje$/.test(w)) return w.slice(0, -1) + "i";               // bytьje -> bytьji
        if (/je$/.test(w)) return w.slice(0, -1) + "i";
        if (/stvo$/.test(w)) return w.slice(0, -1) + "ě";              // -stvo -> -stvě

        if (gender === "masculine") return w + "ě";                   // gord -> gordě
        if (gender === "neuter" && /o$/.test(w)) return w.slice(0, -1) + "ě";

        if (gender === "feminine") {
            if (/ca$/.test(w)) return w.slice(0, -1) + "i";            // okolica -> okolici
            if (/ga$/.test(w)) return w.slice(0, -2) + "dzě";          // usluga -> usludzě
            if (/ka$/.test(w)) return w.slice(0, -2) + "cě";
            if (/a$/.test(w)) return w.slice(0, -1) + "ě";
        }

        return w;
    }

    async function loadInflectionData() {
        if (INFLECT.loaded) return;
        if (INFLECT.loading) return INFLECT.loading;

        INFLECT.loading = (async function () {
            for (const file of DATA_FILES) {
                let rows = [];
                try {
                    const response = await fetch(file, { cache: "no-store" });
                    if (!response.ok) continue;
                    rows = await response.json();
                } catch (e) {
                    continue;
                }

                if (!Array.isArray(rows)) continue;

                rows.forEach(function (row, index) {
                    const polish = String(row && row.polish || "").trim();
                    const slovian = String(row && row.slovian || "").trim();
                    const typeCase = String(row && row["type and case"] || "");
                    if (!polish || !slovian || !typeCase) return;

                    const meta = parseMeta(typeCase);
                    if (meta.wordClass !== "noun") return;

                    const priority = (file === "vuzor.json" ? 500 : 300) + (meta.grammaticalCase === "nominative" ? 80 : 0) - index / 100000;

                    addIndex(INFLECT.exactForms, polish, {
                        polishLemma: polish,
                        slovianLemma: slovian,
                        meta,
                        grammaticalCase: meta.grammaticalCase,
                        number: meta.number,
                        priority
                    });

                    // Z hasłownika bierzemy przede wszystkim nominativus singular jako lemat.
                    if (meta.grammaticalCase === "nominative" && meta.number !== "plural") {
                        addGeneratedForms(polish, slovian, meta, priority);
                    }
                });
            }

            INFLECT.loaded = true;
        })();

        return INFLECT.loading;
    }

    function findEntryForPolishForm(word) {
        const key = foldPolish(word);
        return INFLECT.generatedForms.get(key) || INFLECT.exactForms.get(key) || null;
    }

    function inferNumberFromPolishWord(word, entry) {
        const w = foldPolish(word);
        if (/(ach|ech)$/.test(w)) return "plural";
        if (entry && entry.number) return entry.number;
        if (entry && entry.meta && entry.meta.number) return entry.meta.number;
        return "singular";
    }

    function buildLocativePhrase(prepToken, nounToken) {
        const prep = normalizeKey(prepToken);
        if (!LOCATIVE_PREPOSITIONS_PL.has(prep)) return null;

        const entry = findEntryForPolishForm(nounToken);
        if (!entry || !entry.slovianLemma) return null;

        const number = inferNumberFromPolishWord(nounToken, entry);
        const inflected = inflectSlovianNoun(entry.slovianLemma, entry.meta, "locative", number);
        const newPrep = PREP_PL_TO_SLO.get(prep) || prepToken;

        return applyCaseLike(prepToken, newPrep) + " " + applyCaseLike(nounToken, inflected);
    }

    function findInputLocativePhrases(inputText) {
        const tokens = tokenize(inputText);
        const phrases = [];

        for (let i = 0; i < tokens.length; i++) {
            if (!isWord(tokens[i])) continue;
            const prep = normalizeKey(tokens[i]);
            if (!LOCATIVE_PREPOSITIONS_PL.has(prep)) continue;

            let j = i + 1;
            while (j < tokens.length && isSpace(tokens[j])) j++;
            if (j >= tokens.length || !isWord(tokens[j])) continue;

            const phrase = buildLocativePhrase(tokens[i], tokens[j]);
            if (phrase) phrases.push({ inputStart: i, inputEnd: j, phrase });
        }

        return phrases;
    }

    function replaceFirstOutputLocativePhrase(outputText, replacement) {
        const prepPattern = "(?:vu|v|na|po|pri|ob)";
        const wordPattern = "[\\p{L}\\p{M}0-9'’ěьъǫęšžčćńłóśźż]+";
        const re = new RegExp("\\b" + prepPattern + "\\s+" + wordPattern + "\\b", "iu");
        if (re.test(outputText)) return outputText.replace(re, replacement);
        return replacement;
    }

    function patchOutputFromInput(inputText, outputText) {
        const src = $(SRC_ID) ? $(SRC_ID).value : "";
        const tgt = $(TGT_ID) ? $(TGT_ID).value : "";
        if (src !== "pl" || tgt !== "slo") return outputText;

        const phrases = findInputLocativePhrases(inputText);
        if (!phrases.length) return outputText;

        let patched = String(outputText || "");
        const inputWords = tokenize(inputText).filter(isWord);

        // Jeżeli wpisano samą frazę typu "w grodach", wynik budujemy od zera.
        if (inputWords.length === 2 && phrases.length === 1) {
            const punct = (String(inputText).trim().match(/([.!?…]+)$/u) || ["", ""])[1];
            return fixSpacing(phrases[0].phrase + punct);
        }

        for (const item of phrases) {
            patched = replaceFirstOutputLocativePhrase(patched, item.phrase);
        }

        return fixSpacing(patched);
    }

    function forceHideSuggestionBox() {
        const box = $(SUGGESTION_ID);
        if (!box) return;
        box.style.setProperty("display", "none", "important");
        box.innerHTML = "";
    }

    function installSuggestionBlocker() {
        const style = document.createElement("style");
        style.textContent = "#" + SUGGESTION_ID + "{display:none!important;}";
        document.head.appendChild(style);

        const box = $(SUGGESTION_ID);
        if (box && typeof MutationObserver !== "undefined") {
            const observer = new MutationObserver(forceHideSuggestionBox);
            observer.observe(box, { childList: true, subtree: true, attributes: true, characterData: true });
        }
        forceHideSuggestionBox();
    }

    function getOutputText() {
        const output = $(OUTPUT_ID);
        if (!output) return "";
        return output.value !== undefined ? output.value : output.textContent;
    }

    function setOutputText(text) {
        const output = $(OUTPUT_ID);
        if (!output) return;
        if (output.value !== undefined) output.value = text;
        else output.textContent = text;
    }

    function runNativeTranslation() {
        if (nativeRunLock) return;
        nativeRunLock = true;
        try {
            const candidates = [
                window.translateText,
                window.translate,
                window.performTranslation,
                window.updateTranslation,
                window.doTranslate,
                window.processTranslation,
                window.handleTranslation
            ].filter(fn => typeof fn === "function");

            for (const fn of candidates) {
                try {
                    fn.call(window);
                    return;
                } catch (e) {}
            }

            const input = $(INPUT_ID);
            if (input) input.dispatchEvent(new Event("change", { bubbles: true }));
        } finally {
            nativeRunLock = false;
        }
    }

    function scheduleTranslateAndPatch() {
        window.clearTimeout(patchTimer);
        patchTimer = window.setTimeout(async function () {
            forceHideSuggestionBox();
            await loadInflectionData();
            runNativeTranslation();

            window.setTimeout(function () {
                forceHideSuggestionBox();
                const input = $(INPUT_ID);
                if (!input) return;
                const currentOutput = getOutputText();
                const patched = patchOutputFromInput(input.value, currentOutput);
                if (patched && patched !== currentOutput) setOutputText(patched);
            }, 120);
        }, 30);
    }

    async function readClipboardText() {
        if (navigator.clipboard && typeof navigator.clipboard.readText === "function") {
            try { return await navigator.clipboard.readText(); } catch (e) {}
        }
        return "";
    }

    function insertIntoTextarea(textarea, text) {
        const value = textarea.value || "";
        const start = typeof textarea.selectionStart === "number" ? textarea.selectionStart : value.length;
        const end = typeof textarea.selectionEnd === "number" ? textarea.selectionEnd : value.length;
        textarea.value = value.slice(0, start) + text + value.slice(end);
        const pos = start + String(text).length;
        try { textarea.setSelectionRange(pos, pos); } catch (e) {}
        textarea.focus();
        textarea.dispatchEvent(new Event("input", { bubbles: true }));
        textarea.dispatchEvent(new Event("change", { bubbles: true }));
    }

    window.pasteText = async function () {
        const input = $(INPUT_ID);
        if (!input) return;
        const text = await readClipboardText();
        if (text) insertIntoTextarea(input, text);
        scheduleTranslateAndPatch();
    };

    document.addEventListener("paste", function (event) {
        const input = $(INPUT_ID);
        if (!input || event.target !== input) return;
        window.setTimeout(scheduleTranslateAndPatch, 0);
    }, true);

    document.addEventListener("input", function (event) {
        if (event.target && event.target.id === INPUT_ID) scheduleTranslateAndPatch();
    }, true);

    document.addEventListener("change", function (event) {
        if (event.target && (event.target.id === SRC_ID || event.target.id === TGT_ID || event.target.id === INPUT_ID)) {
            scheduleTranslateAndPatch();
        }
    }, true);

    document.addEventListener("DOMContentLoaded", function () {
        installSuggestionBlocker();
        loadInflectionData().then(scheduleTranslateAndPatch);
    });
})();
