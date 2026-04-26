/* slovo_model.js
 * Runtime JavaScript dla wyuczonego modelu Slovo.
 * Działa w Node.js i w przeglądarce.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.SlovoTranslator = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  const WORD_RE = /[\p{L}\p{M}0-9'’.-]+/u;
  const TOKEN_RE = /([\p{L}\p{M}0-9'’.-]+|\s+|[^\s\p{L}\p{M}0-9'’.-]+)/gu;

  function normalize(text) {
    return String(text ?? "").normalize("NFC").replace(/\s+/g, " ").trim().toLocaleLowerCase("pl");
  }

  function escapeRegExp(text) {
    return String(text).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  function isWord(token) {
    return WORD_RE.test(token);
  }

  function copyCase(source, target) {
    if (!source || !target) return target;
    if (source === source.toLocaleUpperCase("pl") && source !== source.toLocaleLowerCase("pl")) {
      return target.toLocaleUpperCase("pl");
    }
    const first = Array.from(source)[0];
    if (first && first === first.toLocaleUpperCase("pl") && first !== first.toLocaleLowerCase("pl")) {
      const chars = Array.from(target);
      if (!chars.length) return target;
      chars[0] = chars[0].toLocaleUpperCase("pl");
      return chars.join("");
    }
    return target;
  }

  class SlovoTranslator {
    constructor(model) {
      if (!model || !model.lexicon) throw new Error("Brak poprawnego modelu Slovo.");
      this.model = model;
      this.plToSlo = model.lexicon.pl_to_slo || {};
      this.sloToPl = model.lexicon.slo_to_pl || {};
      this.maxPhraseWords = (model.runtimeDefaults && model.runtimeDefaults.maxPhraseWords) || 6;
      this.weights = model.weights || {};
    }

    static async loadFromUrl(url) {
      const response = await fetch(url);
      if (!response.ok) throw new Error(`Nie można pobrać modelu: ${response.status} ${response.statusText}`);
      return new SlovoTranslator(await response.json());
    }

    static loadFromFile(filePath) {
      const fs = require("fs");
      const model = JSON.parse(fs.readFileSync(filePath, "utf8"));
      return new SlovoTranslator(model);
    }

    getMap(direction) {
      if (direction === "slo2pl") return this.sloToPl;
      return this.plToSlo;
    }

    lookup(text, direction = "pl2slo") {
      const key = normalize(text);
      const item = this.getMap(direction)[key];
      return item && item.length ? item[0] : null;
    }

    candidates(text, direction = "pl2slo") {
      return this.getMap(direction)[normalize(text)] || [];
    }

    translate(text, options = {}) {
      const direction = options.direction || "pl2slo";
      const fallback = options.fallback || "guess";
      const original = String(text ?? "");
      const exact = this.lookup(original, direction);
      if (exact) return copyCase(original, exact.target);

      const tokens = original.match(TOKEN_RE) || [original];
      const out = [];
      let i = 0;

      while (i < tokens.length) {
        if (!isWord(tokens[i])) {
          out.push(tokens[i]);
          i++;
          continue;
        }

        let best = null;
        let bestEnd = i;

        for (let words = Math.min(this.maxPhraseWords, 10); words >= 2; words--) {
          let j = i, used = 0, phrase = "";
          while (j < tokens.length && used < words) {
            if (isWord(tokens[j])) {
              phrase += tokens[j];
              used++;
              j++;
              continue;
            }
            if (/^\s+$/.test(tokens[j])) {
              phrase += " ";
              j++;
              continue;
            }
            break;
          }
          if (used === words) {
            const cand = this.lookup(phrase, direction);
            if (cand) {
              best = copyCase(phrase, cand.target);
              bestEnd = j;
              break;
            }
          }
        }

        if (best !== null) {
          out.push(best);
          i = bestEnd;
          continue;
        }

        const tok = tokens[i];
        const cand = this.lookup(tok, direction);
        if (cand) out.push(copyCase(tok, cand.target));
        else out.push(fallback === "guess" && direction === "pl2slo" ? copyCase(tok, this.guessPolishToSlovian(tok)) : tok);
        i++;
      }

      return this.fixSpacing(out.join(""));
    }

    translatePolishToSlovian(text, options = {}) {
      return this.translate(text, { ...options, direction: "pl2slo" });
    }

    translateSlovianToPolish(text, options = {}) {
      return this.translate(text, { ...options, direction: "slo2pl", fallback: options.fallback || "copy" });
    }

    guessPolishToSlovian(word) {
      const src = normalize(word);
      if (!src) return word;

      const suffixRules = this.weights.suffix_pl_to_slo || {};
      const chars = Array.from(src);

      for (let k = Math.min(6, chars.length); k >= 1; k--) {
        const suf = chars.slice(chars.length - k).join("");
        const rule = suffixRules[suf] && suffixRules[suf][0];
        if (rule && rule.value) {
          return chars.slice(0, chars.length - k).join("") + rule.value;
        }
      }

      const charRules = this.weights.char_pl_to_slo || {};
      return chars.map(ch => {
        const r = charRules[ch] && charRules[ch][0];
        return r && r.value ? r.value : ch;
      }).join("");
    }

    fixSpacing(text) {
      return text
        .replace(/\s+([,.;:!?])/g, "$1")
        .replace(/([(\[{])\s+/g, "$1")
        .replace(/\s+([)\]}])/g, "$1")
        .replace(/\s+/g, " ")
        .trim();
    }

    explain(text, options = {}) {
      const direction = options.direction || "pl2slo";
      const exact = this.candidates(text, direction);
      return {
        input: text,
        direction,
        exactCandidates: exact,
        output: this.translate(text, options),
      };
    }
  }

  return SlovoTranslator;
});
