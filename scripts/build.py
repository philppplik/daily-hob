#!/usr/bin/env python3
"""Zero-dependency builder. Source of truth: content/YYYY-MM-DD.json + assets/."""
import json, html, shutil, datetime, base64
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs'
E = lambda s: html.escape(str(s), quote=True)
BASE = 'https://hob.philipp-paulik.de'
AUTHOR = {'@type':'Person','name':'Philipp Paulik','url':'https://philipp-paulik.de','sameAs':['https://github.com/philppplik','https://x.com/philppplik']}
PUBLISHER = {'@type':'Organization','name':'Daily Hob','url':BASE+'/','logo':{'@type':'ImageObject','url':BASE+'/assets/brand/logo.png'}}
LD = lambda o: '<script type="application/ld+json">'+json.dumps(o,ensure_ascii=False).replace('</','<\\/')+'</script>'
ASSET = lambda d,f: f'{BASE}/assets/{d}/{f}'
OUT.mkdir(exist_ok=True)
for encoded in (ROOT/'assets').rglob('*.b64'):
    encoded.with_suffix('').write_bytes(base64.b64decode(encoded.read_text()))
shutil.copy2(ROOT/'style.css', OUT/'style.css')
shutil.copy2(ROOT/'consent.js', OUT/'consent.js')
shutil.copytree(ROOT/'assets', OUT/'assets', dirs_exist_ok=True, ignore=shutil.ignore_patterns('*.b64','*.b64.part*'))
posts = sorted((json.loads(p.read_text()) for p in (ROOT/'content').glob('*.json')), key=lambda p:p['date'], reverse=True)
if not posts: raise ValueError('At least one briefing is required')
for p in posts:
    datetime.date.fromisoformat(p['date'])
    for f in [p[k] for k in ('hero','audio') if p.get(k)] + [s['image'] for s in p['sections'] if 'image' in s] + [g['image'] for g in p.get('gallery',[])]:
        if not (ROOT/'assets'/p['date']/f).is_file(): raise ValueError(f'Missing asset: {f}')
    for s in p['sections']:
        if not s['url'].startswith('https://'): raise ValueError('Sources must use https')
def wrap(title,desc,body,prefix='',path='',image='',ld=None,otype='website',pub=''):
    return f'''<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light dark"><meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#121212" media="(prefers-color-scheme: dark)"><link rel="icon" href="/favicon.ico" sizes="48x48"><link rel="icon" type="image/png" sizes="32x32" href="/assets/icons/icon-32.png"><link rel="icon" type="image/png" sizes="192x192" href="/assets/icons/icon-192.png"><link rel="apple-touch-icon" href="/assets/icons/apple-touch-icon.png"><link rel="manifest" href="/manifest.webmanifest"><script>try{{var t=localStorage.getItem("hob-theme");if(t==="dark"||t==="light")document.documentElement.setAttribute("data-theme",t)}}catch(e){{}}</script><title>{E(title)} · Daily Hob</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="{BASE}/{path}"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:type" content="{otype}"><meta property="og:url" content="{BASE}/{path}"><meta property="og:site_name" content="Daily Hob"><meta property="og:locale" content="de_DE">{f'<meta property="og:image" content="{E(image)}">' if image else ''}<meta name="twitter:card" content="{'summary_large_image' if image else 'summary'}">{f'<meta name="twitter:image" content="{E(image)}">' if image else ''}{f'<meta property="article:published_time" content="{pub}">' if pub else ''}{LD(ld) if ld else ''}<link rel="stylesheet" href="{prefix}style.css"></head><body><a class="skip" href="#main">Zum Inhalt</a><header><nav class="nav" aria-label="Hauptnavigation"><a class="brand" href="{prefix or './'}"><img class="brand-logo" src="{prefix}assets/brand/logo.png" alt="Daily Hob"></a><div class="nav-tools"><span class="nav-right">Dein Briefing. Kein Rauschen.</span><button class="theme-toggle" type="button" aria-label="Dunkelmodus umschalten" aria-pressed="false" title="Hell/Dunkel"><svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg><svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3 7 7 0 0 0 21 12.8z"/></svg></button></div></nav></header><main id="main">{body}</main><section class="nl" aria-labelledby="nl-title"><div><p class="eyebrow">Newsletter</p><h2 id="nl-title">Freitags Signal. Montags Rewind.</h2><p>Zweimal pro Woche das Wichtigste aus dem Daily Hob in dein Postfach: freitags das <strong>Hob Friday Signal</strong>, montags der <strong>Hob Monday Rewind</strong>. Kostenlos, jederzeit abbestellbar.</p></div><form class="nl-form" method="post" novalidate><label class="nl-label">E-Mail-Adresse<input type="email" name="email" autocomplete="email" inputmode="email" placeholder="du@beispiel.de" required></label><div class="nl-hp" aria-hidden="true"><label>Nicht ausfüllen<input type="text" name="website" tabindex="-1" autocomplete="off"></label></div><label class="nl-check"><input type="checkbox" name="consent" required><span>Ja, schick mir das Hob Friday Signal und den Hob Monday Rewind per E-Mail. Du bekommst zuerst eine Bestätigungsmail. Abmelden geht jederzeit mit einem Klick. Mehr dazu in der <a href="{prefix}datenschutz#newsletter">Datenschutzerklärung</a>.</span></label><button class="nl-btn" type="submit">Anmelden</button><p class="nl-msg" role="status" aria-live="polite"></p></form></section><footer><div class="footer"><div><strong>Hob.</strong> Ein guter Start in deinen Kopf.</div><div>Das Briefing-Archiv · KI, Code, Design und mehr</div><nav class="projects" aria-label="Weitere Projekte"><span>Mehr von Philipp:</span><a href="https://pblock.philipp-paulik.de" rel="noopener">pblock</a><a href="https://custmtab.philipp-paulik.de" rel="noopener">custmtab</a><a href="https://zwep.philipp-paulik.de" rel="noopener">zwep</a><a href="https://flower.philipp-paulik.de" rel="noopener">flower</a><a href="https://ct.philipp-paulik.de" rel="noopener">ct</a><a href="https://plane.philipp-paulik.de" rel="noopener">plane</a></nav><nav class="legal" aria-label="Rechtliches"><a href="{prefix}impressum">Impressum</a><a href="{prefix}datenschutz">Datenschutz</a><button class="consent-open" type="button" data-consent-open hidden>Cookie-Einstellungen</button></nav></div></footer><script src="{prefix}consent.js" defer></script><script>(function(){{var r=document.documentElement,b=document.querySelector(".theme-toggle"),m=matchMedia("(prefers-color-scheme: dark)");function d(){{var t=r.getAttribute("data-theme");return t?t==="dark":m.matches}}function u(){{b.setAttribute("aria-pressed",String(d()))}}u();b.addEventListener("click",function(){{var n=d()?"light":"dark";r.setAttribute("data-theme",n);try{{localStorage.setItem("hob-theme",n)}}catch(e){{}}u()}});m.addEventListener&&m.addEventListener("change",u)}})()</script></body></html>'''
def label(p):
    d=datetime.date.fromisoformat(p['date']); return d.strftime('%d.%m.%Y')
def edition_image(p):
    if not p.get('hero'): return ''
    return f'<img class="edition-img" src="assets/{p["date"]}/{E(p["hero"])}" alt="{E(p["heroAlt"])}" width="1300" height="731">'
def media_label(p): return 'Text + Audio' if p.get('audio') else 'Textausgabe'
cards=''
for p in posts:
    cards+=f'''<a class="edition" href="briefings/{p['date']}">{edition_image(p)}<div><div class="meta"><time datetime="{p['date']}">{label(p)}</time><span class="pill">{media_label(p)}</span></div><h2>{E(p['title'])}</h2><p>{E(p['teaser'])}</p><span class="arrow-link">Kopf an. Briefing auf. <span aria-hidden="true">↗</span></span></div></a>'''
index=f'''<section class="intro"><p class="eyebrow">Das Daily-Hob-Briefing-Archiv</p><h1>Weniger Rauschen.<br><span>Mehr Aha.</span></h1><p class="lead">KI, Code und Design. Die Dinge, die hängen bleiben sollen. Zum Lesen, Anhören und später Wiederfinden.</p></section><section aria-label="Alle Ausgaben"><div class="index-label"><h2 class="archive-title">Die Ausgaben</h2><span>{len(posts):02d} im Archiv</span></div>{cards}</section>'''
idx_desc='Das Daily-Hob-Briefing-Archiv. KI, Code und Design zum Lesen und Anhören.'
idx_img=next((ASSET(p['date'],p['hero']) for p in posts if p.get('hero')),'')
idx_ld=[{'@context':'https://schema.org','@type':'CollectionPage','name':'Daily Hob','description':idx_desc,'url':BASE+'/','inLanguage':'de','isPartOf':{'@type':'WebSite','name':'Daily Hob','url':BASE+'/','publisher':PUBLISHER},'mainEntity':{'@type':'ItemList','itemListOrder':'https://schema.org/ItemListOrderDescending','numberOfItems':len(posts),'itemListElement':[{'@type':'ListItem','position':i,'url':f'{BASE}/briefings/{p["date"]}','name':p['title']} for i,p in enumerate(posts,1)]}},{'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Daily Hob','item':BASE+'/'}]}]
(OUT/'index.html').write_text(wrap('Weniger Rauschen. Mehr Aha.', idx_desc, index, '', '', idx_img, idx_ld))
(OUT/'briefings').mkdir(exist_ok=True)
for p in posts:
    ap='../assets/'+p['date']+'/'
    toc=''.join(f'<li><a href="#story-{n}">{n:02d} / {E(s.get("short") or s["title"])}<span class="toc-tag">{E(s["category"].split(" / ")[0])}</span></a></li>' for n,s in enumerate(p['sections'],1))
    stories=''
    for n,s in enumerate(p['sections'],1):
        im=f'<img loading="lazy" src="{ap}{E(s["image"])}" alt="{E(s["imageAlt"])}">' if 'image' in s else ''
        stories+=f'''<section class="story" id="story-{n}"><p class="eyebrow">{n:02d} / {E(s['category'])}</p><h2>{E(s['title'])}</h2><p>{E(s['body'])}</p>{im}<p class="take">{E(s['takeaway'])}</p><a class="arrow-link" href="{E(s['url'])}" target="_blank" rel="noopener noreferrer">{E(s['cta'])}</a><p class="source">{E(s['source'])}</p></section>'''
    gallery=''
    if p.get('gallery'):
        gallery='<details class="gallery"><summary>Aus dem Bildarchiv dieser Ausgabe +</summary>'+''.join(f'<figure><img loading="lazy" src="{ap}{E(g["image"])}" alt="{E(g["alt"])}"><figcaption>{E(g["caption"])}</figcaption></figure>' for g in p['gallery'])+'</details>'
    audio=f'''<section class="listen" id="audio"><p class="eyebrow">Augen zu. Kopf an.</p><h2>Lieber auf die Ohren?</h2><p>{E(p.get('audioLabel',''))}</p><audio controls preload="metadata" aria-label="{E(p['title'])} anhören"><source src="{ap}{E(p.get('audio',''))}" type="audio/mpeg">Dein Browser unterstützt den Audio-Player nicht.</audio><a href="{ap}{E(p.get('audio',''))}" download>MP3 für unterwegs herunterladen ↓</a></section>'''
    if not p.get('audio'): audio=''
    hero = f'<figure class="hero"><img src="{ap}{E(p["hero"])}" alt="{E(p["heroAlt"])}" width="1300" height="731"><figcaption>{E(p["heroCaption"])}</figcaption></figure>' if p.get('hero') else ''
    audio_toc = '<li><a href="#audio">▶ Audio anhören</a></li>' if p.get('audio') else ''
    archive_note = f'<p class="source"><a href="{E(p["archiveUrl"])}" target="_blank" rel="noopener noreferrer">Auswahl im datierten Tagesarchiv nachvollziehen ↗</a></p>' if p.get('archiveUrl') else ''
    body=f'''<a class="back" href="../">← Alle Ausgaben</a><section class="detail-intro"><p class="eyebrow">{E(p['title'])} / {len(p['sections'])} Catches</p><h1>{E(p['headline'])}</h1><p class="lead">{E(p['intro'])}</p></section>{hero}<div class="body-grid"><aside class="toc"><p class="eyebrow">In dieser Ausgabe</p><ol>{toc}{audio_toc}</ol></aside><article>{stories}{gallery}{audio}<p class="notes">{E(p['notes'])}</p>{archive_note}</article></div>'''
    url=f'{BASE}/briefings/{p["date"]}'
    himg=ASSET(p['date'],p['hero']) if p.get('hero') else ''
    art={'@context':'https://schema.org','@type':'NewsArticle','headline':p['headline'].replace('\n',' ')[:110],'alternativeHeadline':p['title'],'description':p['teaser'],'datePublished':p['date'],'dateModified':p.get('modified',p['date']),'inLanguage':'de','url':url,'mainEntityOfPage':{'@type':'WebPage','@id':url},'author':AUTHOR,'publisher':PUBLISHER}
    if himg: art['image']=[himg]
    crumbs={'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Daily Hob','item':BASE+'/'},{'@type':'ListItem','position':2,'name':p['title'],'item':url}]}
    (OUT/'briefings'/f'{p["date"]}.html').write_text(wrap(p['title'],p['teaser'],body,'../',f'briefings/{p["date"]}',himg,[art,crumbs],'article',p['date']))
for slug,title,desc in (('impressum','Impressum','Anbieterkennzeichnung nach § 5 DDG für das Daily-Hob-Briefing-Archiv.'),('datenschutz','Datenschutzerklärung','Datenschutzerklärung für das Daily-Hob-Briefing-Archiv.')):
    frag=(ROOT/'content'/f'legal-{slug}.html').read_text(encoding='utf-8')
    (OUT/f'{slug}.html').write_text(wrap(title,desc,f'<a class="back" href="./">← Alle Ausgaben</a><article class="legal-page">{frag}</article>','',slug))
NLP='<a class="back" href="./">← Alle Ausgaben</a><section class="detail-intro"><p class="eyebrow">Newsletter</p><h1 id="nl-status-title">Daily Hob im Postfach</h1><p class="lead" id="nl-status-text">Trag dich unten ein. Du bekommst zuerst eine Bestätigungsmail.</p></section>'
(OUT/'newsletter.html').write_text(wrap('Newsletter','Hob Friday Signal und Hob Monday Rewind: das Daily Hob zweimal pro Woche per E-Mail.',NLP,'','newsletter'))
urls=[(BASE+'/',max(p['date'] for p in posts))]+[(f'{BASE}/briefings/{p["date"]}',p.get('modified',p['date'])) for p in posts]+[(f'{BASE}/newsletter',None),(f'{BASE}/impressum',None),(f'{BASE}/datenschutz',None)]
(OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{E(u)}</loc>'+(f'<lastmod>{m}</lastmod>' if m else '')+'</url>' for u,m in urls)+'</urlset>\n')
(OUT/'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n')
(OUT/'CNAME').write_text('hob.philipp-paulik.de\n') if False else None
shutil.copy2(ROOT/'assets'/'icons'/'favicon.ico', OUT/'favicon.ico')
(OUT/'manifest.webmanifest').write_text(json.dumps({'name':'Daily Hob','short_name':'Hob','lang':'de','start_url':'/','display':'browser','background_color':'#ffffff','theme_color':'#121212','icons':[{'src':'/assets/icons/icon-192.png','sizes':'192x192','type':'image/png'},{'src':'/assets/icons/icon-512.png','sizes':'512x512','type':'image/png'}]},ensure_ascii=False))
(OUT/'.nojekyll').touch()
print(f'Built {len(posts)} briefing(s) into {OUT}')
