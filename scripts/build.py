#!/usr/bin/env python3
"""Zero-dependency builder. Source of truth: content/YYYY-MM-DD.json + assets/."""
import json, html, shutil, datetime, base64
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs'
E = lambda s: html.escape(str(s), quote=True)
OUT.mkdir(exist_ok=True)
for encoded in (ROOT/'assets').rglob('*.b64'):
    encoded.with_suffix('').write_bytes(base64.b64decode(encoded.read_text()))
shutil.copy2(ROOT/'style.css', OUT/'style.css')
shutil.copytree(ROOT/'assets', OUT/'assets', dirs_exist_ok=True, ignore=shutil.ignore_patterns('*.b64','*.b64.part*'))
posts = sorted((json.loads(p.read_text()) for p in (ROOT/'content').glob('*.json')), key=lambda p:p['date'], reverse=True)
if not posts: raise ValueError('At least one briefing is required')
for p in posts:
    datetime.date.fromisoformat(p['date'])
    for f in [p['hero'],p['audio']] + [s['image'] for s in p['sections'] if 'image' in s] + [g['image'] for g in p.get('gallery',[])]:
        if not (ROOT/'assets'/p['date']/f).is_file(): raise ValueError(f'Missing asset: {f}')
    for s in p['sections']:
        if not s['url'].startswith('https://'): raise ValueError('Sources must use https')
def wrap(title,desc,body,prefix=''):
    return f'''<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>{E(title)} · Daily Hob</title><meta name="description" content="{E(desc)}"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:type" content="website"><link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%23181818'/%3E%3Ctext x='9' y='24' font-family='Arial' font-size='24' fill='white'%3Eh%3C/text%3E%3C/svg%3E"><link rel="stylesheet" href="{prefix}style.css"></head><body><a class="skip" href="#main">Zum Inhalt</a><header><nav class="nav" aria-label="Hauptnavigation"><a class="brand" href="{prefix}index.html"><img class="brand-logo" src="{prefix}assets/brand/logo.png" alt="Daily Hob"></a><span class="nav-right">Dein Briefing. Kein Rauschen.</span></nav></header><main id="main">{body}</main><footer><div class="footer"><div><strong>Hob.</strong> Ein guter Start in deinen Kopf.</div><div>Ein persönliches Briefing-Archiv · Text + Audio</div></div></footer></body></html>'''
def label(p):
    d=datetime.date.fromisoformat(p['date']); return d.strftime('%d.%m.%Y')
cards=''
for p in posts:
    cards+=f'''<a class="edition" href="briefings/{p['date']}.html"><img class="edition-img" src="assets/{p['date']}/{E(p['hero'])}" alt="{E(p['heroAlt'])}" width="1300" height="731"><div><div class="meta"><time datetime="{p['date']}">{label(p)}</time><span class="pill">Text + Audio</span></div><h2>{E(p['title'])}</h2><p>{E(p['teaser'])}</p><span class="arrow-link">Kopf an. Briefing auf. <span aria-hidden="true">↗</span></span></div></a>'''
index=f'''<section class="intro"><p class="eyebrow">Das persönliche Briefing-Archiv</p><h1>Weniger Rauschen.<br><span>Mehr Aha.</span></h1><p class="lead">KI, Code und Design. Die Dinge, die hängen bleiben sollen. Zum Lesen, Anhören und später Wiederfinden.</p></section><section aria-label="Alle Ausgaben"><div class="index-label"><h2 class="archive-title">Die Ausgaben</h2><span>{len(posts):02d} im Archiv</span></div>{cards}</section>'''
(OUT/'index.html').write_text(wrap('Weniger Rauschen. Mehr Aha.', 'Das persönliche Briefing-Archiv. KI, Code und Design zum Lesen und Anhören.', index))
(OUT/'briefings').mkdir(exist_ok=True)
for p in posts:
    ap='../assets/'+p['date']+'/'
    toc=''.join(f'<li><a href="#story-{n}">{n:02d} / {E(s["category"].split(" / ")[0])}</a></li>' for n,s in enumerate(p['sections'],1))
    stories=''
    for n,s in enumerate(p['sections'],1):
        im=f'<img loading="lazy" src="{ap}{E(s["image"])}" alt="{E(s["imageAlt"])}">' if 'image' in s else ''
        stories+=f'''<section class="story" id="story-{n}"><p class="eyebrow">{n:02d} / {E(s['category'])}</p><h2>{E(s['title'])}</h2><p>{E(s['body'])}</p>{im}<p class="take">{E(s['takeaway'])}</p><a class="arrow-link" href="{E(s['url'])}" target="_blank" rel="noopener noreferrer">{E(s['cta'])}</a><p class="source">{E(s['source'])}</p></section>'''
    gallery=''
    if p.get('gallery'):
        gallery='<details class="gallery"><summary>Aus dem Bildarchiv dieser Ausgabe +</summary>'+''.join(f'<figure><img loading="lazy" src="{ap}{E(g["image"])}" alt="{E(g["alt"])}"><figcaption>{E(g["caption"])}</figcaption></figure>' for g in p['gallery'])+'</details>'
    audio=f'''<section class="listen" id="audio"><p class="eyebrow">Augen zu. Kopf an.</p><h2>Lieber auf die Ohren?</h2><p>{E(p['audioLabel'])}</p><audio controls preload="metadata" aria-label="{E(p['title'])} anhören"><source src="{ap}{E(p['audio'])}" type="audio/mpeg">Dein Browser unterstützt den Audio-Player nicht.</audio><a href="{ap}{E(p['audio'])}" download>MP3 für unterwegs herunterladen ↓</a></section>'''
    body=f'''<a class="back" href="../index.html">← Alle Ausgaben</a><section class="detail-intro"><p class="eyebrow">{E(p['title'])} / {len(p['sections'])} Catches</p><h1>{E(p['headline'])}</h1><p class="lead">{E(p['intro'])}</p></section><figure class="hero"><img src="{ap}{E(p['hero'])}" alt="{E(p['heroAlt'])}" width="1300" height="731"><figcaption>{E(p['heroCaption'])}</figcaption></figure><div class="body-grid"><aside class="toc"><p class="eyebrow">In dieser Ausgabe</p><ol>{toc}<li><a href="#audio">▶ Audio anhören</a></li></ol></aside><article>{stories}{gallery}{audio}<p class="notes">{E(p['notes'])}</p></article></div>'''
    (OUT/'briefings'/f'{p["date"]}.html').write_text(wrap(p['title'],p['teaser'],body,'../'))
(OUT/'.nojekyll').touch()
print(f'Built {len(posts)} briefing(s) into {OUT}')
