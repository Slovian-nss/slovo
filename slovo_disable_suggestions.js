/* slovo_disable_suggestions.js
 * Całkowicie wyłącza customową sugestię poprawy w interfejsie Slovo.
 * Korekta przeglądarkowa/Google psuje formy fleksyjne typu: Bez miasta, W grodach itd.
 */
(function () {
    "use strict";

    const SUGGESTION_IDS = ["suggestionBox"];
    const BLOCK_SELECTORS = [
        "#suggestionBox",
        ".suggestionBox",
        ".suggestion-box",
        "[data-slovo-suggestion]"
    ];

    function forceHideElement(el) {
        if (!el) return;
        try {
            el.innerHTML = "";
            el.textContent = "";
            el.hidden = true;
            el.setAttribute("aria-hidden", "true");
            el.setAttribute("data-disabled", "true");
            el.style.setProperty("display", "none", "important");
            el.style.setProperty("visibility", "hidden", "important");
            el.style.setProperty("opacity", "0", "important");
            el.style.setProperty("height", "0", "important");
            el.style.setProperty("min-height", "0", "important");
            el.style.setProperty("max-height", "0", "important");
            el.style.setProperty("margin", "0", "important");
            el.style.setProperty("padding", "0", "important");
            el.style.setProperty("border", "0", "important");
            el.style.setProperty("overflow", "hidden", "important");
            el.style.setProperty("pointer-events", "none", "important");
        } catch (e) {}
    }

    function killSuggestions() {
        for (const id of SUGGESTION_IDS) {
            forceHideElement(document.getElementById(id));
        }
        for (const selector of BLOCK_SELECTORS) {
            try {
                document.querySelectorAll(selector).forEach(forceHideElement);
            } catch (e) {}
        }
    }

    function installPermanentCss() {
        if (document.getElementById("slovo-disable-suggestions-style")) return;
        const style = document.createElement("style");
        style.id = "slovo-disable-suggestions-style";
        style.textContent = BLOCK_SELECTORS.join(",") + "{display:none!important;visibility:hidden!important;opacity:0!important;height:0!important;min-height:0!important;max-height:0!important;margin:0!important;padding:0!important;border:0!important;overflow:hidden!important;pointer-events:none!important;}";
        document.head.appendChild(style);
    }

    function disableKnownGlobalCorrectionFunctions() {
        const noop = function () { return false; };
        const names = [
            "showSuggestion",
            "showCorrection",
            "showCorrectionSuggestion",
            "updateSuggestion",
            "checkSpelling",
            "correctInput",
            "applyCorrection",
            "suggestCorrection"
        ];

        for (const name of names) {
            try {
                if (typeof window[name] === "function") window[name] = noop;
            } catch (e) {}
        }
    }

    function installObserver() {
        if (typeof MutationObserver === "undefined") return;
        const observer = new MutationObserver(function () {
            killSuggestions();
            disableKnownGlobalCorrectionFunctions();
        });
        observer.observe(document.documentElement, {
            childList: true,
            subtree: true,
            attributes: true,
            characterData: true,
            attributeFilter: ["style", "class", "hidden", "data-disabled"]
        });
    }

    function boot() {
        installPermanentCss();
        disableKnownGlobalCorrectionFunctions();
        killSuggestions();
        installObserver();

        // Dodatkowy bezpiecznik, bo stary kod potrafi pokazać sugestię po async fetchu.
        let ticks = 0;
        const fast = window.setInterval(function () {
            ticks += 1;
            killSuggestions();
            disableKnownGlobalCorrectionFunctions();
            if (ticks > 200) window.clearInterval(fast);
        }, 50);

        window.setInterval(function () {
            killSuggestions();
            disableKnownGlobalCorrectionFunctions();
        }, 1000);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", boot);
    } else {
        boot();
    }
})();
