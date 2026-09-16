# focus on me — site

Site static, 8 limbi (EN la rădăcină, restul în foldere: ro/, fr/, de/, es/, it/, pt/, nl/).

## Cum editezi
- Texte: `_build/i18n/<limbă>.json` (una pe limbă, aceleași chei).
- Pagini legale, câte un folder pe limbă: `_build/legal/<limbă>/privacy-policy.html`, `terms.html`, `refund-policy.html`.
  Versiunea din `_build/legal/en/` e cea de referință; celelalte sunt traduceri (site-ul afișează o notă că engleza prevalează).
  Textele marcate `<span class="placeholder">` (dată, formă juridică, adresă, CUI, nr. registru) apar galben pe site și trebuie completate în toate cele 8 foldere.
- Stil / script: `assets/style.css`, `assets/main.js`. Poze: `assets/img/`.
- Butoanele de store: în `_build/build.py`, funcția `store_buttons` (acum „Coming soon”; când ai link-urile, pune-le acolo).

## Regenerezi paginile
```bash
python3 _build/build.py
```

## Previzualizare locală
```bash
python3 -m http.server 8765
```
apoi deschide http://localhost:8765

`_old/` conține site-ul vechi, poate fi șters.
