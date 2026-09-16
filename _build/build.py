#!/usr/bin/env python3
"""Generates the focus on me static site from _build/i18n/*.json and _build/legal/*.html.
Run:  python3 _build/build.py
Output: index.html + contact.html (EN) at the root, one folder per other language,
        legal pages (EN only) at the root."""
import json, re, html, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
I18N = Path(__file__).resolve().parent / "i18n"
LEGAL = Path(__file__).resolve().parent / "legal"
LANG_ORDER = ["en", "ro", "fr", "de", "es", "it", "pt", "nl"]
EMAIL = "contact@focusonme.fashion"
SITE = "https://focusonme.fashion"
V = str(int(time.time()))  # cache-busting for css/js

langs = {c: json.loads((I18N / f"{c}.json").read_text(encoding="utf-8")) for c in LANG_ORDER}

# ── icons ─────────────────────────────────────────────────────────────
def ic(path, sw=1.8):
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{path}</svg>')

ICON = {
    "clock": ic('<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>'),
    "grid": ic('<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>'),
    "shield": ic('<path d="M12 21s8-3.6 8-10V5l-8-3-8 3v6c0 6.4 8 10 8 10z"/><path d="M9 12l2 2 4-4"/>'),
    "share": ic('<path d="M4 12v7a1 1 0 001 1h14a1 1 0 001-1v-7"/><path d="M16 6l-4-4-4 4"/><path d="M12 2v13"/>'),
    "globe": ic('<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3a14 14 0 010 18a14 14 0 010-18z"/>'),
    "upload": ic('<rect x="3" y="4" width="18" height="16" rx="3"/><path d="M8 20l4-5 3 3 2-2 4 4"/><circle cx="9" cy="9" r="1.6"/><path d="M15 3v5M12.5 5.5L15 3l2.5 2.5"/>'),
    "spark": ic('<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M19 17l.7 2.3L22 20l-2.3.7L19 23l-.7-2.3L16 20l2.3-.7z"/>'),
    "chev": '<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>',
    "plus": ic('<path d="M12 5v14M5 12h14"/>', 2.4),
    "burger": ic('<path d="M4 7h16M4 12h16M4 17h16"/>', 2),
    "mail": ic('<rect x="3" y="5" width="18" height="14" rx="3"/><path d="M3 8l9 6 9-6"/>'),
    "apple": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16.4 12.7c0-2.5 2-3.7 2.1-3.8-1.2-1.7-3-1.9-3.6-2-1.5-.2-3 .9-3.8.9-.8 0-2-.9-3.3-.8-1.7 0-3.2 1-4.1 2.5-1.8 3-.5 7.5 1.3 10 .9 1.2 1.9 2.6 3.2 2.5 1.3-.1 1.8-.8 3.3-.8 1.5 0 2 .8 3.3.8 1.4 0 2.3-1.2 3.1-2.5 1-1.4 1.4-2.8 1.4-2.9-.1 0-2.9-1.1-2.9-4.9zM14 5.3c.7-.8 1.2-2 1-3.1-1 0-2.2.7-2.9 1.5-.6.7-1.2 1.9-1 3 1.1.1 2.2-.6 2.9-1.4z"/></svg>',
    "play": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M4 3.5v17c0 .5.5.8.9.5l9.6-8.5-9.6-8.5c-.4-.3-.9 0-.9.5z" opacity=".95"/><path d="M14.5 12.5l3.7 3.3 2.4-1.4c.6-.3.6-1.2 0-1.5l-2.4-1.4-3.7 3.3z" opacity=".75"/><path d="M4.9 21l9.6-8.5-3.4-3-6.2 11.5z" opacity=".6"/><path d="M4.9 3l6.2 11.5 3.4-3L4.9 3z" opacity=".85"/></svg>',
    "logo": '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4.5"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/></svg>',
}
FEATURE_ICONS = ["upload", "clock", "grid", "shield", "share", "globe", "spark"]

def e(s): return html.escape(s, quote=True)

# ── shared chrome ─────────────────────────────────────────────────────
def lang_menu(cur, pfx, page):
    items = []
    for c in LANG_ORDER:
        href = f"{pfx}{page}" if c == "en" else f"{pfx}{c}/{page}"
        cls = ' class="active"' if c == cur else ""
        items.append(f'<a href="{href}" data-lang="{c}"{cls} hreflang="{c}">{langs[c]["name"]}</a>')
    t = langs[cur]
    return (f'<details class="lang"><summary aria-label="{e(t["nav"]["language"])}">{ICON["globe"]}'
            f'<span class="name">{cur.upper()}</span>{ICON["chev"]}</summary>'
            f'<div class="lang-menu"><div class="lbl">{e(t["nav"]["language"])}</div>{"".join(items)}</div></details>')

def nav(t, cur, pfx, page, inner=False):
    home = f"{pfx}index.html" if cur == "en" else f"{pfx}{cur}/index.html"
    home_rel = "index.html" if not inner or page == "contact.html" else home
    if inner:
        links = f'<div class="nav-links"><a href="{home_rel}">{e(t["nav"]["back"])}</a></div>'
        mobile = f'<div class="mobile-menu"><a href="{home_rel}">{e(t["nav"]["back"])}</a></div>'
    else:
        n = t["nav"]
        links = (f'<div class="nav-links"><a href="#how">{e(n["how"])}</a><a href="#features">{e(n["features"])}</a>'
                 f'<a href="#credits">{e(n["credits"])}</a><a href="#faq">{e(n["faq"])}</a></div>')
        mobile = (f'<div class="mobile-menu"><a href="#how">{e(n["how"])}</a><a href="#features">{e(n["features"])}</a>'
                  f'<a href="#credits">{e(n["credits"])}</a><a href="#faq">{e(n["faq"])}</a><a href="#download">{e(n["cta"])}</a></div>')
    cta = "" if inner else f'<a class="btn btn-dark btn-sm" href="#download">{e(t["nav"]["cta"])}</a>'
    burger = "" if inner else f'<button class="burger" aria-label="Menu">{ICON["burger"]}</button>'
    return (f'<nav class="nav"><div class="container nav-inner">'
            f'<a class="logo" href="{home_rel}"><i>{ICON["logo"]}</i>focus on me</a>{links}'
            f'<div class="nav-right">{lang_menu(cur, pfx, page)}{cta}{burger}</div></div></nav>{mobile}')

def footer(t, cur, pfx, page):
    f = t["footer"]
    home = "index.html"
    ll = []
    for c in LANG_ORDER:
        href = f"{pfx}{page}" if c == "en" else f"{pfx}{c}/{page}"
        act = ' class="active"' if c == cur else ""
        ll.append(f'<a href="{href}" data-lang="{c}" hreflang="{c}"{act}>{langs[c]["name"]}</a>')
    return f'''<footer><div class="container">
  <div class="foot">
    <div><a class="logo" href="{home}"><i>{ICON["logo"]}</i>focus on me</a><p>{e(t["hero"]["sub"])}</p></div>
    <div><h4>Legal</h4><ul>
      <li><a href="privacy-policy.html">{e(f["privacy"])}</a></li>
      <li><a href="terms.html">{e(f["terms"])}</a></li>
      <li><a href="refund-policy.html">{e(f["refund"])}</a></li>
      <li><a href="contact.html">{e(f["contact"])}</a></li>
    </ul></div>
    <div><h4>{e(t["nav"]["language"])}</h4><div class="langs">{"".join(ll)}</div></div>
  </div>
  <div class="foot-bottom"><span>{e(f["copy"])}</span><span>{e(f["legal_note"])}</span></div>
</div></footer>'''

def head(t, cur, pfx, page, title, desc, root=False, canonical_path=""):
    alts = "".join(
        f'<link rel="alternate" hreflang="{c}" href="{SITE}/{"" if c == "en" else c + "/"}{page}">' for c in LANG_ORDER)
    alts += f'<link rel="alternate" hreflang="x-default" href="{SITE}/{page}">'
    root_attr = f' data-root="1" data-langs="{",".join(LANG_ORDER)}"' if root else ""
    return f'''<!DOCTYPE html>
<html lang="{t["html_lang"]}"{root_attr}>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:image" content="{SITE}/assets/img/hero.png">
<meta name="theme-color" content="#ffffff">
{alts}
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{pfx}assets/style.css?v={V}">
</head>
<body>
'''

def tail(pfx):
    return f'<script src="{pfx}assets/main.js?v={V}"></script>\n</body>\n</html>\n'

def store_buttons(t, soon=True):
    h = t["hero"]
    cls = "store soon" if soon else "store"
    tag = "span" if soon else "a"
    return (f'<div class="stores">'
            f'<{tag} class="{cls}" aria-disabled="true">{ICON["apple"]}<span><small>{e(h["soon"])}</small><b>{e(h["appstore"])}</b></span></{tag}>'
            f'<{tag} class="{cls}" aria-disabled="true">{ICON["play"]}<span><small>{e(h["soon"])}</small><b>{e(h["play"])}</b></span></{tag}>'
            f'</div>')

# ── home page ─────────────────────────────────────────────────────────
def home(cur):
    t = langs[cur]; pfx = "" if cur == "en" else "../"; img = f"{pfx}assets/img/"
    h, s, how, fe, cr, fq, cta = t["hero"], t["stats"], t["how"], t["features"], t["credits"], t["faq"], t["cta"]

    stats = "".join(f'<div class="stat"><b class="count">{e(x["num"])}</b><span>{e(x["label"])}</span></div>' for x in s)

    steps = "".join(
        f'<div class="step reveal d{i}"><div class="step-shot"><img src="{img}pas{i+1}.png" alt="{e(st["title"])}" loading="lazy"></div>'
        f'<div class="step-num">0{i+1}</div><h3>{e(st["title"])}</h3><p>{e(st["desc"])}</p></div>'
        for i, st in enumerate(how["steps"]))

    decos = ["", "30s", "4k+", "", "", "", ""]
    wide = {0, 3}
    cards = []
    for i, f in enumerate(fe["items"]):
        deco = ""; extra = ""
        if i == 0:
            deco = '<div class="deco upload">+</div>'
        elif i == 5:
            extra = '<div class="flags">' + "".join(f"<span>{c.upper()}</span>" for c in LANG_ORDER) + "</div>"
        elif decos[i]:
            deco = f'<div class="deco">{decos[i]}</div>'
        cards.append(f'<div class="card{" wide" if i in wide else ""} reveal d{i % 3}">{deco}'
                     f'<div class="icon">{ICON[FEATURE_ICONS[i]]}</div>'
                     f'<div class="body">{extra}<h3>{e(f["title"])}</h3><p>{e(f["desc"])}</p></div></div>')

    credits = "".join(
        f'<div class="credit reveal d{i}"><div class="n">0{i+1}</div><h3>{e(c["title"])}</h3><p>{e(c["desc"])}</p></div>'
        for i, c in enumerate(cr["items"]))

    faqs = "".join(
        f'<details class="faq-item"><summary>{e(q["q"])}<span class="plus">{ICON["plus"]}</span></summary><p>{e(q["a"])}</p></details>'
        for q in fq["items"])

    body = f'''
<header class="container">
  <section class="hero">
    <div class="hero-text">
      <span class="badge"><i></i>{e(h["badge"])}</span>
      <h1>{e(h["h1a"])}<br><span class="light">{e(h["h1b"])}</span></h1>
      <p class="lede">{e(h["sub"])}</p>
      {store_buttons(t)}
      <p class="note">{e(h["note"])}</p>
    </div>
    <div class="hero-visual">
      <div class="blob"></div>
      <div class="phone"><img src="{img}hero.png" alt="focus on me app" fetchpriority="high"></div>
      <div class="chip chip-1"><i>{ICON["grid"]}</i><span class="count">{e(h["chip1"])}</span></div>
      <div class="chip chip-2"><i>{ICON["clock"]}</i>{e(h["chip2"])}</div>
    </div>
  </section>
  <div class="stats reveal">{stats}</div>
</header>

<main>
<section class="section" id="how">
  <div class="container"><div class="band"><div class="band-inner"><div class="container">
    <div class="section-head reveal">
      <div class="eyebrow">{e(how["eyebrow"])}</div>
      <h2 class="h2">{e(how["title_a"])}<br><span class="light">{e(how["title_b"])}</span></h2>
      <p class="lede">{e(how["sub"])}</p>
    </div>
    <div class="steps">{steps}</div>
  </div></div></div></div>
</section>

<section class="section" id="features" style="padding-top:0">
  <div class="container">
    <div class="section-head reveal">
      <div class="eyebrow">{e(fe["eyebrow"])}</div>
      <h2 class="h2">{e(fe["title_a"])}<br><span class="light">{e(fe["title_b"])}</span></h2>
    </div>
    <div class="bento">{"".join(cards)}</div>
  </div>
</section>

<section class="section" id="credits" style="padding-top:0">
  <div class="container"><div class="band"><div class="band-inner"><div class="container">
    <div class="section-head reveal">
      <div class="eyebrow">{e(cr["eyebrow"])}</div>
      <h2 class="h2">{e(cr["title_a"])}<br><span class="light">{e(cr["title_b"])}</span></h2>
      <p class="lede">{e(cr["sub"])}</p>
    </div>
    <div class="credits">{credits}</div>
    <p class="credits-note reveal">{e(cr["note"])} <a href="refund-policy.html">{e(cr["note_link"])} →</a></p>
  </div></div></div></div>
</section>

<section class="section" id="faq" style="padding-top:0">
  <div class="container faq">
    <div class="section-head reveal">
      <div class="eyebrow">{e(fq["eyebrow"])}</div>
      <h2 class="h2">{e(fq["title_a"])}<br><span class="light">{e(fq["title_b"])}</span></h2>
    </div>
    <div class="faq-list reveal d1">{faqs}</div>
  </div>
</section>

<section class="section" id="download" style="padding-top:0">
  <div class="container"><div class="cta on-dark reveal">
    <h2>{e(cta["title_a"])} <span class="light">{e(cta["title_b"])}</span></h2>
    <p>{e(cta["sub"])}</p>
    {store_buttons(t)}
  </div></div>
</section>
</main>
'''
    return (head(t, cur, pfx, "index.html", t["meta"]["title"], t["meta"]["description"], root=(cur == "en"))
            + nav(t, cur, pfx, "index.html") + body + footer(t, cur, pfx, "index.html") + tail(pfx))

# ── contact page ──────────────────────────────────────────────────────
def contact(cur):
    t = langs[cur]; c = t["contact"]; pfx = "" if cur == "en" else "../"
    body = f'''
<main class="page"><div class="container">
  <div class="page-head"><h1>{e(c["title"])}</h1><div class="meta">{e(c["meta"])}</div></div>
  <p class="lede" style="margin:0 0 28px">{e(c["intro"])}</p>
  <div class="contact-grid">
    <div class="contact-card">
      <div class="lbl">{e(c["label"])}</div>
      <div class="mail">{EMAIL}</div>
      <div class="desc">{e(c["desc"])}</div>
      <a class="btn btn-dark" href="mailto:{EMAIL}">{ICON["mail"]}{e(c["button"])}</a>
    </div>
    <div class="contact-hint">
      <h3>{e(c["hint_title"])}</h3>
      <p>{e(c["hint"])} <a href="refund-policy.html">{e(t["footer"]["refund"])} →</a></p>
    </div>
  </div>
</div></main>
'''
    title = f'{c["title"]} — focus on me'
    return (head(t, cur, pfx, "contact.html", title, c["intro"], root=(cur == "en"))
            + nav(t, cur, pfx, "contact.html", inner=True) + body + footer(t, cur, pfx, "contact.html") + tail(pfx))

# ── legal pages (one per language, content from _build/legal/<lang>/) ──
LEGAL_FILES = ["privacy-policy.html", "terms.html", "refund-policy.html"]
LEGAL_KEYS = {"privacy-policy.html": "privacy", "terms.html": "terms", "refund-policy.html": "refund"}

def legal(cur, fname):
    t = langs[cur]; pfx = "" if cur == "en" else "../"
    src = (LEGAL / cur / fname).read_text(encoding="utf-8")
    m = re.search(r"<body[^>]*>(.*)</body>", src, re.S)
    inner = (m.group(1) if m else src).strip()
    inner = re.sub(r"<table>", '<div class="table-wrap"><table>', inner)
    inner = re.sub(r"</table>", "</table></div>", inner)
    h1 = re.search(r"<h1>(.*?)</h1>", inner, re.S)
    title = h1.group(1).strip() if h1 else t["footer"][LEGAL_KEYS[fname]]
    updated = re.search(r'<p class="updated">(.*?)</p>', inner, re.S)
    inner = re.sub(r'<h1>.*?</h1>\s*', "", inner, count=1, flags=re.S)
    inner = re.sub(r'<p class="updated">.*?</p>\s*', "", inner, count=1, flags=re.S)
    tabs = "".join(f'<a href="{f}"' + (' class="active"' if f == fname else "") + f'>{e(t["footer"][LEGAL_KEYS[f]])}</a>' for f in LEGAL_FILES)
    note = "" if cur == "en" else f'<p class="legal-note">{e(t["footer"]["legal_note"])} <a href="{pfx}{fname}" hreflang="en">English</a></p>'
    body = f'''
<main class="page"><div class="container">
  <div class="legal-tabs">{tabs}</div>
  <div class="page-head"><h1>{title}</h1><div class="meta">{updated.group(1) if updated else ""} &nbsp;·&nbsp; Cubo Software</div></div>
  {note}
  <div class="prose">{inner}</div>
</div></main>
'''
    desc = f"{title} — focus on me"
    return (head(t, cur, pfx, fname, f"{title} — focus on me", desc)
            + nav(t, cur, pfx, fname, inner=True) + body + footer(t, cur, pfx, fname) + tail(pfx))

# ── write ─────────────────────────────────────────────────────────────
written = []
for c in LANG_ORDER:
    out = ROOT if c == "en" else ROOT / c
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(home(c), encoding="utf-8"); written.append(out / "index.html")
    (out / "contact.html").write_text(contact(c), encoding="utf-8"); written.append(out / "contact.html")
    for f in LEGAL_FILES:
        (out / f).write_text(legal(c, f), encoding="utf-8"); written.append(out / f)
print(f"wrote {len(written)} pages")
