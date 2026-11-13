#!/usr/bin/env python3
"""Build a fully static research website with Python's standard library.

Usage:
  python scripts/build.py
  python scripts/build.py --base-url https://sunghongpark.ai
No network access or third-party Python packages are required.
"""
from __future__ import annotations
import argparse
import html
import json
import math
import re
import shutil
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--base-url', help='Public HTTPS origin, with an optional project path.')
parser.add_argument('--output', default=str(ROOT / 'site'), help='Generated output directory.')
args = parser.parse_args()
OUT = Path(args.output).resolve()
if OUT in (ROOT, ROOT / 'content', ROOT / 'design', ROOT / 'scripts'):
    parser.error('Use a separate output directory, not a source directory.')

def load(name: str):
    return json.loads((ROOT / 'content' / f'{name}.json').read_text(encoding='utf-8'))

P = load('profile')
PUBS = load('publications')
ONGOING = load('ongoing')
ARCHIVE = load('archive')
BASE = (args.base_url or P['base_url']).rstrip('/')
u = urlparse(BASE)
if u.scheme != 'https' or not u.hostname or u.query or u.fragment or u.username or u.password or u.port:
    parser.error('--base-url must be an HTTPS site URL without credentials, query, fragment, or port.')
if not re.fullmatch(r'[A-Za-z0-9.-]+', u.hostname):
    parser.error('Hostname must be ASCII (use punycode for internationalized domains).')
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'assets').mkdir(exist_ok=True)
for name in ['styles.css', 'site.js', 'theme.js']:
    shutil.copyfile(ROOT / 'design' / name, OUT / 'assets' / name)
if (ROOT / 'design' / 'og-card.png').exists():
    shutil.copyfile(ROOT / 'design' / 'og-card.png', OUT / 'assets' / 'og-card.png')
# Self-hosted, open-licensed fonts and their licence texts. No font service is contacted;
# if design/fonts is removed, the stylesheet falls back to system fonts.
FONT_DIR = ROOT / 'design' / 'fonts'
FONT_FILES = sorted(f for f in FONT_DIR.iterdir() if f.suffix in ('.woff2', '.txt')) if FONT_DIR.is_dir() else []
if FONT_FILES:
    (OUT / 'assets' / 'fonts').mkdir(exist_ok=True)
    for font in FONT_FILES:
        shutil.copyfile(font, OUT / 'assets' / 'fonts' / font.name)
PRELOAD = [f.name for f in FONT_FILES if f.name in ('inter-latin-wght-normal.woff2', 'space-grotesk-latin-wght-normal.woff2')]
FONT_PRELOAD = ''.join(f'<link rel="preload" href="assets/fonts/{name}" as="font" type="font/woff2" crossorigin>' for name in PRELOAD)

E = lambda value: html.escape(str(value), quote=True)
PUB_BY_ID = {paper['id']: paper for paper in PUBS}
if len(PUB_BY_ID) != len(PUBS):
    raise ValueError('Duplicate publication IDs.')
for paper in PUBS:
    assert re.fullmatch(r'[a-z0-9-]+', paper['id']), 'Publication IDs must be URL-safe.'
    assert re.match(r'^10\.\d{4,9}/\S+$', paper['doi']), f"Invalid DOI: {paper['doi']}"
for field in ['github', 'scholar', 'cv_url', 'source_url']:
    assert urlparse(P[field]).scheme == 'https', f'{field} must use HTTPS.'

ICON_PATHS = {
    'arrow': '<path d="M5 12h14M13 6l6 6-6 6"/>',
    'up-right': '<path d="M6 18 18 6M6 6h12v12"/>',
    'download': '<path d="M12 3v12m-5-5 5 5 5-5M5 16v4h14v-4"/>',
    'copy': '<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V4H4v12h4"/>',
    'search': '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
    'moon': '<path d="M20 14.2A8.3 8.3 0 0 1 9.8 4a8.3 8.3 0 1 0 10.2 10.2Z"/>',
    'sun': '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    'menu': '<path d="M4 7h16M4 12h16M4 17h16"/>',
    'close': '<path d="m6 6 12 12M6 18 18 6"/>',
    'mail': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 6 9 7 9-7"/>',
    'quote': '<path d="M5 11h5v7H3v-6c0-4 2-6 6-6M16 11h5v7h-7v-6c0-4 2-6 6-6"/>',
    'print': '<path d="M7 7V3h10v4M7 16H4V8h16v8h-3M7 13h10v8H7z"/>',
}
def icon(name='arrow', extra=''):
    cls = 'icon ' + extra if extra else 'icon'
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{ICON_PATHS[name]}</svg>'

def external(url, label, cls='text-link', kind='up-right'):
    return f'<a class="{E(cls)}" href="{E(url)}" target="_blank" rel="noopener noreferrer">{label}{icon(kind)}</a>'

# Signal Graph design: headlines end in a "hot" dot, and the three research
# directions are always named by shape and colour together (see design/styles.css).
DOT = '<span class="dot">.</span>'
TOPICS = {'Graph learning': 'graph', 'Biomedical AI': 'biomedical', 'Domain adaptation': 'adaptation'}
def marker(label):
    return f'<span class="marker" data-topic="{TOPICS.get(label, "other")}" aria-hidden="true"></span>'

def tags(values, markers=True):
    return '<div class="tag-list">' + ''.join(f'<span class="tag">{marker(t) if markers else ""}{E(t)}</span>' for t in values) + '</div>'

def authors(value):
    return E(value).replace('Sunghong Park', '<strong>Sunghong Park</strong>').replace('†', '<sup>†</sup>').replace('*', '<sup>*</sup>')

def plain_authors(value):
    return value.replace('†', '').replace('*', '')

def bibtex(paper):
    author_list = []
    for name in plain_authors(paper['authors']).split(', '):
        parts = name.rsplit(' ', 1)
        author_list.append(f'{parts[1]}, {parts[0]}' if len(parts) == 2 else name)
    def clean(value):
        return str(value).replace('’', "'").replace('–', '--').replace('&', r'\&')
    fields = {'title': '{' + clean(paper['title']) + '}', 'author': ' and '.join(author_list),
              'journal': paper['journal'], 'year': paper['year'], 'volume': paper['volume']}
    if paper.get('issue'):
        fields['number'] = paper['issue']
    fields.update({'pages': clean(paper['pages']), 'doi': paper['doi'], 'url': 'https://doi.org/' + paper['doi']})
    return '@article{' + paper['id'] + ',\n' + ',\n'.join('  ' + key + ' = {' + str(val) + '}' for key, val in fields.items()) + '\n}'

CITATIONS = {}
for p in PUBS:
    volume = p['volume'] + (f"({p['issue']})" if p.get('issue') else '')
    text = f"{plain_authors(p['authors'])}. ({p['year']}). {p['title']}. {p['journal']}, {volume}, {p['pages']}. https://doi.org/{p['doi']}"
    CITATIONS[p['id']] = {'title': p['title'], 'text': text, 'bibtex': bibtex(p)}
(OUT / 'assets' / 'site-data.js').write_text('window.SITE_DATA = ' + json.dumps({'citations': CITATIONS}, ensure_ascii=False).replace('<', '\\u003c') + ';\n', encoding='utf-8')
(OUT / 'publications.bib').write_text('% Public website bibliography, reviewed ' + P['content_reviewed'] + '\n% Includes published journal articles only; excludes manuscripts under review.\n\n' + '\n\n'.join(bibtex(p) for p in PUBS) + '\n', encoding='utf-8')

def mini_visual(kind):
    """Small schematic for one research direction. Colours come from the stylesheet."""
    svg = '<svg viewBox="0 0 280 120" aria-hidden="true">'
    if kind == 'graph':
        nodes = [(35,62),(69,25),(94,92),(128,52),(176,19),(184,90),(227,49),(250,89),(225,10)]
        pairs = [(0,1),(0,2),(0,3),(1,3),(1,4),(2,3),(2,5),(3,4),(3,5),(3,6),(4,6),(4,8),(5,6),(5,7),(6,7),(6,8)]
        svg += '<path class="mv-edge" d="' + ''.join(f'M{nodes[a][0]} {nodes[a][1]}L{nodes[b][0]} {nodes[b][1]}' for a,b in pairs) + '"/>'
        for i,(x,y) in enumerate(nodes):
            svg += f'<circle class="{"mv-node-solid" if i in (0,3,6) else "mv-node"}" cx="{x}" cy="{y}" r="{8 if i==3 else 5}"/>'
    elif kind == 'biomedical':
        svg += '<path class="mv-guide" d="M95 30v50M140 20v50M185 30v50M140 40v50"/>'
        for layer, offset in enumerate((0,25,50), start=1):
            svg += f'<path class="mv-layer mv-layer-{layer}" d="M50 {30+offset} 140 {7+offset} 230 {30+offset} 140 {53+offset}Z"/>'
        for offset in (0,25,50):
            for x,y in [(95,30),(140,20),(185,30),(140,40)]:
                svg += f'<circle class="mv-node-solid" cx="{x}" cy="{y+offset}" r="3.5"/>'
    else:
        svg += '<ellipse class="mv-ring" cx="72" cy="60" rx="49" ry="36"/><ellipse class="mv-ring" cx="208" cy="60" rx="49" ry="36"/>'
        for x,y in [(48,55),(68,38),(88,48),(65,77),(93,73)]:
            svg += f'<circle class="mv-node-solid" cx="{x}" cy="{y}" r="4.5"/>'
        for x,y in [(190,51),(216,38),(230,63),(198,78),(212,62)]:
            svg += f'<circle class="mv-node" cx="{x}" cy="{y}" r="4.5"/>'
        svg += '<path class="mv-arrow" d="M126 48h28m-6-5 6 5-6 5M154 74h-28m6-5-6 5 6 5"/>'
    return '<div class="mini-visual">'+svg+'</svg></div>'

def network_map():
    """Conceptual figure: three kinds of data (flat discs) meet in one learned representation."""
    discs = [(150,140,105),(372,150,98),(255,335,100)]
    hub = (260,208)
    edges = [
        'M150 140L98 102M150 140L142 74M150 140L196 96M150 140L88 162M150 140L128 196M150 140L188 188M98 102L142 74M142 74L196 96M88 162L128 196M128 196L188 188M196 96L216 146M188 188L216 146M98 102L88 162',
        'M372 150L330 110M372 150L378 88M372 150L424 118M372 150L436 170M372 150L398 208M372 150L346 200M330 110L378 88M378 88L424 118M424 118L436 170M398 208L346 200M346 200L318 160M330 110L318 160',
        'M255 335L205 300M255 335L250 272M255 335L304 296M255 335L322 348M255 335L286 392M255 335L228 396M255 335L190 356M205 300L250 272M304 296L322 348M286 392L228 396M228 396L190 356M205 300L190 356',
    ]
    hollow = [(98,102),(142,74),(88,162),(188,188),(216,146),(330,110),(424,118),(398,208),(318,160),(205,300),(304,296),(286,392),(190,356)]
    solid = [(196,96),(128,196),(378,88),(436,170),(346,200),(250,272),(322,348),(228,396)]
    s = '<svg id="research-map-svg" class="network-svg" viewBox="0 0 520 470" role="img" aria-labelledby="map-title map-desc" data-mode="graph"><title id="map-title">Connecting heterogeneous biomedical data through graph learning</title><desc id="map-desc">A conceptual network connects protein, imaging and clinical data around an AI representation. This is a schematic, not experimental data.</desc>'
    s += ''.join(f'<circle class="disc disc-{i}" cx="{x}" cy="{y}" r="{r}"/>' for i,(x,y,r) in enumerate(discs, start=1))
    s += '<g class="map-edges">' + ''.join(f'<path d="{d}"/>' for d in edges) + '</g>'
    s += '<path class="map-bridges" d="' + ''.join(f'M{x} {y}L{hub[0]} {hub[1]}' for x,y,_ in discs) + '"/>'
    s += '<g class="map-nodes">' + ''.join(f'<circle cx="{x}" cy="{y}" r="5"/>' for x,y in hollow) + '</g>'
    s += '<g class="map-nodes-solid">' + ''.join(f'<circle cx="{x}" cy="{y}" r="5.5"/>' for x,y in solid) + '</g>'
    s += '<g class="map-centers">' + ''.join(f'<circle cx="{x}" cy="{y}" r="9"/>' for x,y,_ in discs) + '</g>'
    s += f'<circle class="hub-halo" cx="{hub[0]}" cy="{hub[1]}" r="58"/><circle class="hub-ring" cx="{hub[0]}" cy="{hub[1]}" r="48"/><circle class="hub" cx="{hub[0]}" cy="{hub[1]}" r="38"/><text class="hub-word" x="{hub[0]}" y="{hub[1]+10}" text-anchor="middle">AI</text>'
    s += '<text class="map-label" x="150" y="22" text-anchor="middle">PROTEINS</text><text class="map-label" x="372" y="38" text-anchor="middle">IMAGING</text><text class="map-label" x="255" y="458" text-anchor="middle">CLINICAL DATA</text></svg>'
    return f'''<figure class="research-map"><div class="map-top"><span>From data to understanding</span><span class="map-index">Fig. 01</span></div>{s}
<div class="map-tabs js-only" role="group" aria-label="Explore the research map"><button type="button" data-map-mode="graph" aria-pressed="true">Graph learning</button><button type="button" data-map-mode="biomedical" aria-pressed="false">Biomedical AI</button><button type="button" data-map-mode="adaptation" aria-pressed="false">Domain adaptation</button></div>
<figcaption class="map-caption"><div id="map-description" aria-live="polite">Learning useful representations from connected observations.</div><span>Conceptual research map · not experimental data</span></figcaption></figure>'''

BRAND_MARK = '<span class="brand-mark" aria-hidden="true">sp<span>.</span></span>'

def header(active):
    links=[('index.html','Home'),('research.html','Research'),('publications.html','Publications'),('projects.html','Projects'),('cv.html','About / CV')]
    nav=''.join(f'<a href="{href}"'+(' aria-current="page"' if href==active else '')+f'><span>{label}</span></a>' for href,label in links)
    return f'''<a href="#main" class="skip-link">Skip to content</a><header class="site-header"><div class="container header-inner"><a class="brand" href="index.html" aria-label="Sunghong Park — home">{BRAND_MARK}<span class="brand-name">Sunghong Park</span></a><nav id="main-navigation" class="main-nav" aria-label="Main navigation">{nav}<a href="#contact" class="mobile-contact-link"><span>Contact</span></a></nav><div class="header-actions"><button type="button" class="icon-button theme-toggle js-only" data-theme-toggle aria-label="Switch to dark theme" aria-pressed="false">{icon('moon','icon-moon')}{icon('sun','icon-sun')}</button><a class="header-contact" href="#contact">Let's connect{icon('up-right')}</a><button type="button" class="icon-button menu-toggle js-only" data-menu-toggle aria-controls="main-navigation" aria-expanded="false" aria-label="Open navigation">{icon('menu','icon-menu')}{icon('close','icon-close')}</button></div></div></header><noscript><div class="no-js-note"><p>All research content is available below. Enable JavaScript for search, citation copying, and theme controls.</p></div></noscript>'''

def contact():
    return f'''<section class="contact-section on-sky" id="contact" aria-labelledby="contact-heading"><div class="container contact-layout"><div class="contact-copy-block"><span class="eyebrow">Start a conversation</span><h2 id="contact-heading">Good research begins<br>with a connection{DOT}</h2><p>For research discussions and collaboration in graph learning, domain adaptation, and biomedical AI.</p></div><div class="contact-actions"><a class="email-link" href="mailto:{E(P['email'])}">{E(P['email'])}{icon('up-right')}</a><button type="button" class="contact-copy js-only" data-copy-email="{E(P['email'])}">{icon('copy')}Copy email address</button><p class="contact-affiliation">{E(P['department'])} · {E(P['institution_short'])}</p></div></div></section>'''

def footer():
    return f'''<footer class="site-footer on-ink"><div class="container"><div class="footer-top"><a class="footer-name" href="index.html">Sunghong Park{DOT}</a><nav class="footer-links" aria-label="Footer navigation"><a href="research.html">Research</a><a href="archive.html">Full archive</a><a href="{E(P['scholar'])}" target="_blank" rel="noopener noreferrer">Google Scholar{icon('up-right')}</a><a href="{E(P['github'])}" target="_blank" rel="noopener noreferrer">GitHub{icon('up-right')}</a></nav></div><div class="footer-bottom"><span>© {P['content_reviewed'][:4]} Sunghong Park · {E(P['location'])}</span><span>Research × AI · Content reviewed {E(P['content_reviewed'])}</span></div></div></footer><div id="toast" class="toast" role="status" aria-live="polite" hidden></div>'''

def dialog():
    return f'''<dialog id="citation-dialog" class="citation-dialog" aria-labelledby="citation-heading"><div class="dialog-heading"><h2 id="citation-heading">Cite this work{DOT}</h2><button type="button" class="icon-button" data-close-dialog aria-label="Close citation dialog">{icon('close')}</button></div><p class="dialog-title" id="citation-paper-title"></p><div class="citation-tabs" role="group" aria-label="Citation format"><button type="button" data-citation-format="text" aria-pressed="true">Plain text</button><button type="button" data-citation-format="bibtex" aria-pressed="false">BibTeX</button></div><label for="citation-text" class="search-label">Citation text</label><textarea id="citation-text" class="citation-text" readonly spellcheck="false"></textarea><div class="dialog-footer"><p id="citation-feedback" aria-live="polite">Bibliographic data is maintained locally. Check publisher metadata for submission-specific citation requirements.</p><button type="button" class="btn btn-primary btn-small" data-copy-citation>{icon('copy')}Copy citation</button></div></dialog>'''

pages = []
def page(path, title, description, body, *, citation_dialog=False):
    canonical=BASE+'/' + ('' if path=='index.html' else path)
    page_title = (title+' — ' if title else '') + 'Sunghong Park | Graph Learning & Biomedical AI'
    schema={'@context':'https://schema.org','@type':'Person','name':P['name'],'alternateName':P['name_ko'],'url':BASE+'/', 'jobTitle':P['role'],'affiliation':{'@type':'Organization','name':P['institution']},'sameAs':[P['scholar'],P['github']],'knowsAbout':['Graph representation learning','Semi-supervised learning','Domain adaptation','Biomedical artificial intelligence']}
    base_tag = f'<base href="{E(u.path.rstrip("/") + "/")}">' if path=='404.html' else ''
    robots = '<meta name="robots" content="noindex">' if path=='404.html' else ''
    document=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">{base_tag}<title>{E(page_title)}</title><meta name="description" content="{E(description)}"><meta name="author" content="Sunghong Park"><meta name="theme-color" content="#3a3d44"><meta name="referrer" content="strict-origin-when-cross-origin">{robots}<link rel="canonical" href="{E(canonical)}"><meta property="og:type" content="website"><meta property="og:site_name" content="Sunghong Park"><meta property="og:title" content="{E(page_title)}"><meta property="og:description" content="{E(description)}"><meta property="og:url" content="{E(canonical)}"><meta property="og:image" content="{E(BASE)}/assets/og-card.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="Sunghong Park — Graph Learning and Biomedical AI"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="assets/favicon.svg" type="image/svg+xml">{FONT_PRELOAD}<link rel="stylesheet" href="assets/styles.css"><script src="assets/theme.js"></script><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False).replace('<',chr(92)+'u003c')}</script><script src="assets/site-data.js" defer></script><script src="assets/site.js" defer></script></head>
<body>{header(path)}<main id="main">{body}</main>{contact()}{footer()}{dialog() if citation_dialog else ''}</body></html>'''
    # Apply saved theme before CSS becomes render-blocking.
    document=document.replace('<link rel="stylesheet" href="assets/styles.css"><script src="assets/theme.js"></script>', '<script src="assets/theme.js"></script><link rel="stylesheet" href="assets/styles.css">')
    (OUT/path).write_text(document,encoding='utf-8')
    if path != '404.html': pages.append(path)

def intro(kicker,title,description,extra='',aside=''):
    """Page masthead: Ink band with the page title; `extra` is a meta row under a rule."""
    return f'<section class="masthead on-ink"><div class="container page-intro"><div class="intro-head"><div class="intro-main"><span class="eyebrow">{kicker}</span><h1>{title}</h1><p class="lead">{description}</p></div>{aside}</div>{extra}</div></section>'

def research_cards():
    result='<div class="research-grid">'
    for item in P['research']:
        result+=f'''<article class="research-card" data-direction="{item['id']}"><div class="direction-panel"><span class="direction-number">{item['number']}</span>{mini_visual(item['id'])}</div><h3><a href="research.html#{item['id']}">{E(item['title'])}</a></h3><p>{E(item['description'])}</p><div class="card-bottom"><span class="label"><span class="marker" data-topic="{item['id']}" aria-hidden="true"></span>{E(item['methods'][0])}</span><span class="card-arrow" aria-hidden="true">{icon('up-right')}</span></div></article>'''
    return result+'</div>'

def selected_papers():
    result='<div class="selected-list">'
    for p in PUBS:
        if not p['featured']: continue
        result+=f'''<article class="selected-paper"><div class="selected-meta"><strong>{E(p['journal'])}</strong><span>{p['year']} · {E(p['label'])}</span></div><div class="selected-body"><h3><a href="publications.html#{p['id']}">{E(p['title'])}</a></h3><p>{E(p['summary'])}</p>{tags(p['tags'])}</div><a href="https://doi.org/{E(p['doi'])}" class="card-arrow" target="_blank" rel="noopener noreferrer" aria-label="Read {E(p['title'])} on the publisher website">{icon('up-right')}</a></article>'''
    return result+'</div>'

def year_plot():
    """Dot plot of published articles per year, counted from publications.json."""
    years=[p['year'] for p in PUBS]
    first,last=min(years),max(years)
    cols=''
    for year in range(first,last+1):
        count=years.count(year)
        dots='<span class="year-dot"></span>'*count if count else '<span class="year-none"></span>'
        cols+=f'<div class="year-col"><div class="year-dots">{dots}</div><span>{str(year)[2:]}</span></div>'
    summary=', '.join(f'{years.count(year)} in {year}' for year in sorted(set(years)))
    return f'<div class="year-plot"><p class="label">Articles<br>per year<br>{first}–{last}</p><div class="year-cols" role="img" aria-label="Published journal articles per year: {summary}.">{cols}</div></div>'

def grant_timeline():
    """Funding periods on a year axis, read from the grant dates; omitted if a date does not parse."""
    months={name:index for index,name in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split())}
    spans=[]
    for g in P['grants']:
        m=re.fullmatch(r'([A-Z][a-z]{2}) (\d{4}) — ([A-Z][a-z]{2}) (\d{4})',g['dates'])
        if not m or m.group(1) not in months or m.group(3) not in months:
            return ''
        spans.append((int(m.group(2))+months[m.group(1)]/12, int(m.group(4))+(months[m.group(3)]+1)/12, g))
    if not spans:
        return ''
    spans.sort(key=lambda span: span[0])
    first=math.floor(spans[0][0]); last=math.ceil(max(span[1] for span in spans))
    if last<=first:
        return ''
    bars=''
    for start,end,g in spans:
        cls='gt-span is-active' if g['status']=='Active' else 'gt-span'
        bars+=f'<div class="{cls}" style="left:{(start-first)/(last-first)*100:.2f}%;width:{(end-start)/(last-first)*100:.2f}%"><span class="gt-label">{E(g["status"].split()[0])}</span><span class="gt-bar"></span></div>'
    years=''.join(f'<span>{year}</span>' for year in range(first,last))
    label='NRF funding timeline. '+' '.join(f'{g["dates"]}: {g["status"]}.' for _,_,g in spans)
    return f'<div class="grant-timeline" role="img" aria-label="{E(label)}"><div class="gt-track">{bars}</div><div class="gt-years" style="--years:{last-first}">{years}</div></div>'

# 1. Homepage.
grant=P['grants'][0]
update_html=''.join(f'<article class="update-item"><time>{E(i["date"])}</time><div><span class="update-type">{E(i["label"])}</span><p><a href="{E(i["href"])}">{E(i["text"])}</a></p></div></article>' for i in P['updates'])
home=f'''<section class="hero on-ink"><div class="container"><div class="hero-layout"><div class="hero-copy"><div class="identity-line"><span class="status-dot"></span>Graph learning × Biomedical AI</div><h1>Learning from<br><span class="key">connections.</span></h1><p class="name-line">Sunghong Park, Ph.D.</p><p class="hero-description">{E(P['intro'])}</p><div class="btn-group"><a class="btn btn-primary" href="research.html">Explore my research{icon('arrow')}</a><a class="btn" href="publications.html">View publications{icon('up-right')}</a></div><div class="social-links">{external(P['scholar'],'Google Scholar','')}{external(P['github'],'GitHub','')}{external(P['cv_url'],'Download CV','','download')}</div></div>{network_map()}</div><div class="stat-row"><div class="stat"><span class="stat-number">{len(PUBS):02}</span><span class="stat-label">Peer-reviewed <br>journal articles</span></div><div class="stat"><span class="stat-number">{len(ARCHIVE['patents']):02}</span><span class="stat-label">Patent applications <br>KR · PCT · US</span></div><div class="stat"><span class="stat-number">{len(P['grants']):02}</span><span class="stat-label">NRF research grants <br>as Principal Investigator</span></div><div class="stat stat-affiliation"><span class="stat-kicker">Current position</span><strong>{E(P['role'])}</strong><span>{E(P['institution_short'])} · {E(P['department'])}</span></div></div></div></section>
<div class="latest-strip on-sky"><div class="container latest-inner"><span class="latest-label">Latest update</span><span class="latest-date">2026.09</span><p>New chapter at KAIST · Life Science Research Institute</p><a class="icon-link" href="cv.html#experience" aria-label="View the KAIST appointment in my CV">{icon('arrow')}</a></div></div>
<section class="section"><div class="container"><div class="section-heading"><div><span class="eyebrow">Research directions</span><h2>Structure. Transfer.<br>Understanding{DOT}</h2></div><p>Three connected directions for learning from complex biomedical data.</p></div>{research_cards()}</div></section>
<section class="section section-ruled"><div class="container"><div class="section-heading"><div><span class="eyebrow">Selected publications</span><h2>Ideas into evidence{DOT}</h2></div><a class="text-link" href="publications.html">All {len(PUBS)} journal articles{icon('arrow')}</a></div>{selected_papers()}<p class="paper-note">Published work only. Manuscripts under review are listed separately in the publication archive.</p></div></section>
<section class="section section-ruled"><div class="container"><div class="section-heading"><div><span class="eyebrow">Currently exploring</span><h2>The next questions{DOT}</h2></div><a class="text-link" href="projects.html">Research projects{icon('arrow')}</a></div><div class="focus-grid"><article class="focus-card on-ink"><div class="focus-meta"><span>NRF · Principal Investigator</span><span>2026—2029</span></div><span class="status status-active">Active research</span><h3>{E(grant['title'])}</h3><p>Connecting multimodal diagnostic estimation with long-term prognostic prediction. An NRF-supported investigation into explainable brain aging models.</p><a class="text-link" href="projects.html#brain-age">Explore the project{icon('arrow')}</a></article><div class="updates"><h3>Notes &amp; updates</h3>{update_html}</div></div></div></section>'''
page('index.html','',P['description'],home)

# 2. Research.
direction_nav='<nav class="intro-meta direction-nav" aria-label="Research directions">'+''.join(f'<a href="#{item["id"]}"><span class="marker" data-topic="{item["id"]}" aria-hidden="true"></span>{item["number"]} · {E(item["title"])}</a>' for item in P['research'])+'</nav>'
research=intro('Research philosophy','Learning what to share.<br><span class="key">Preserving what matters.</span>','My work asks how learning systems can use relationships, transfer information across domains, and incorporate biological knowledge without losing meaningful differences.',direction_nav)
research+='<div class="container research-list">'
for item in P['research']:
    related=''.join(f'<a class="related-work" href="publications.html#{pid}"><span>{E(PUB_BY_ID[pid]["title"])} <span class="muted">({PUB_BY_ID[pid]["year"]})</span></span>{icon("up-right")}</a>' for pid in item['publications'])
    research+=f'<section class="research-detail" id="{item["id"]}" data-direction="{item["id"]}"><div class="direction-panel"><span class="direction-number">{item["number"]}</span>{mini_visual(item["id"])}</div><div class="research-body"><span class="eyebrow"><span class="marker" data-topic="{item["id"]}" aria-hidden="true"></span>Direction {item["number"]}</span><h2>{E(item["title"])}</h2><p>{E(item["description"])}</p><div class="research-question on-sky"><span class="label">Research question</span><p>{E(item["question"])}</p></div>{tags(item["methods"], markers=False)}<div class="related-works"><span class="label">Related published work</span>{related}</div></div></section>'
research+='</div><section class="section section-ruled"><div class="container"><span class="eyebrow">An organizing perspective</span><h2>From method to biomedical question'+DOT+'</h2><div class="principle-grid"><div class="principle"><div class="principle-node"><span>01</span></div><span class="label">Represent</span><h3>Use the structure</h3><p>Represent relationships among observations and biological entities rather than treating every feature in isolation.</p></div><div class="principle"><div class="principle-node"><span>02</span></div><span class="label">Transfer</span><h3>Respect the differences</h3><p>Study which information can be shared across populations, modalities, and observation times.</p></div><div class="principle"><div class="principle-node"><span>03</span><i aria-hidden="true"></i></div><span class="label">Interpret</span><h3>Connect back to biology</h3><p>Relate model representations to disease heterogeneity, biological pathways, and candidate biomarkers.</p></div></div></div></section>'
page('research.html','Research','Research directions in graph representation learning, explainable biomedical AI, and domain adaptation.',research)

# 3. Publications, built as HTML and enhanced by local filtering.
extra=f'<div class="intro-meta intro-bottom"><div class="intro-facts"><p>{len(PUBS)} published journal articles · {len(ONGOING["manuscripts"])} manuscript under review</p><p class="small">† Co-first author · * Corresponding author</p><a class="btn btn-small" href="publications.bib" download>{icon("download")}Download BibTeX</a></div>{year_plot()}</div>'
publications=intro('Publication archive','Methods, findings,<br><span class="key">and the work behind them.</span>','A chronological collection of peer-reviewed journal articles. Search by title, author, or venue, and narrow the list by year or research direction.',extra)
publications+='<div class="container page-content">'

def filter_panel(categories, years=None, *, noun='journal articles', placeholder='Title, author, keyword, or venue', archive=False):
    yearfield=''
    if years:
        yearfield='<div><label class="search-label" for="year-filter">Year</label><select id="year-filter" data-year><option value="all">All years</option>'+''.join(f'<option value="{year}">{year}</option>' for year in sorted(set(years),reverse=True))+'</select></div>'
    chips=''.join(f'<button type="button" class="filter-chip" data-filter="{E(v)}" aria-pressed="{str(v=="all").lower()}">{marker(v) if not archive and v!="all" else ""}{E(label)}</button>' for v,label in categories)
    return f'''<form class="filter-panel on-sky js-only" data-filter-root data-result-noun="{E(noun)}" role="search" aria-label="Search {E(noun)}"><div class="filter-top"><div><label class="search-label" for="record-search">Search {E(noun)}</label><div class="search-field">{icon('search')}<input type="search" id="record-search" data-search placeholder="{E(placeholder)}" autocomplete="off"></div></div>{yearfield}</div><div class="filter-chips" role="group" aria-label="Filter by {'record type' if archive else 'research direction'}">{chips}</div></form><div class="result-bar js-only"><span data-result-count role="status" aria-live="polite"></span><button type="button" class="reset-button" data-reset>Reset filters</button></div><div class="no-results" data-empty hidden><h3>No matching records</h3><p>Try another keyword, year, or category—or reset the filters.</p></div>'''

publications+=filter_panel([('all','All research'),('Graph learning','Graph learning'),('Biomedical AI','Biomedical AI'),('Domain adaptation','Domain adaptation'),('Other applications','Other applications')],[p['year'] for p in PUBS])
publications+='<div class="record-list">'
for p in PUBS:
    volume=p['volume']+(f"({p['issue']})" if p.get('issue') else '')
    publications+=f'''<article class="pub-item" id="{p['id']}" data-filter-item data-year="{p['year']}" data-topics="{E('|'.join(p['tags']))}"><div class="pub-year">{p['year']}</div><div class="pub-body"><h2><a href="https://doi.org/{E(p['doi'])}" target="_blank" rel="noopener noreferrer">{E(p['title'])}</a></h2><p class="pub-authors">{authors(p['authors'])}</p><p class="pub-venue">{E(p['journal'])} <span class="mono">· {E(volume)} · {E(p['pages'])}</span></p><div class="pub-actions">{external('https://doi.org/'+p['doi'],'Read paper','cite-btn')}<button type="button" class="cite-btn js-only" data-cite="{p['id']}" aria-label="Cite {E(p['title'])}">{icon('quote')}Cite / BibTeX</button>{tags(p['tags'])}</div></div></article>'''
publications+='</div><section class="manuscript-panel" id="under-review"><span class="eyebrow">Separate from published work</span><h2>Manuscripts under review</h2>'
for p in ONGOING['manuscripts']:
    publications+=f'<article><span class="status status-neutral">{E(p["status"])}</span><h3>{E(p["title"])}</h3><p class="pub-authors">{authors(p["authors"])}</p><p class="pub-venue">Submitted to {E(p["venue"])}</p><p class="paper-note">{E(p["note"])} Status inherited from the public website reviewed {E(P["content_reviewed"])}.</p></article>'
publications+='</section><p class="paper-note">Research directions are editorial tags. Publication status is not updated automatically. The downloadable bibliography excludes work under review.</p></div>'
page('publications.html','Publications','Search published journal articles by Sunghong Park, with DOI links, plain-text citations, and BibTeX export.',publications,citation_dialog=True)

# 4. Projects.
jump_links=f'<nav class="jump-links" aria-label="On this page"><a href="#funded">Funded research · {len(P["grants"])}</a><a href="#ongoing">Ongoing investigations · {len(ONGOING["projects"])}</a></nav>'
projects=intro('Research in progress','The questions<br><span class="key">driving the next chapter.</span>','Funded research programs and ongoing investigations. Active work is presented as a research direction, not as a completed or clinically validated result.',f'<div class="intro-meta intro-bottom">{grant_timeline()}{jump_links}</div>')
projects+=f'<section class="section" id="funded"><div class="container"><div class="section-heading"><h2>Funded research{DOT}</h2><p>Principal Investigator · NRF Basic Science Research Program</p></div>'
for g in P['grants']:
    active=g['status']=='Active'
    projects+=f'<article class="grant{" grant-active on-sky" if active else ""}" id="{g["id"]}"><div class="grant-meta"><span class="status {"status-active" if active else "status-done"}">{E(g["status"])}</span><p class="funding-body">{E(g["funder"])}</p><p class="small">{E(g["role"])}<br>{E(g["dates"])}</p><p class="grant-id">{E(g["number"])}</p></div><div class="grant-body"><h3>{E(g["title"])}</h3><p>{E(g["description"])}</p><p class="grant-title"><strong>Official project title</strong><br>{E(g["official_title"])}</p><p class="paper-note">{E(g["program"])}</p></div></article>'
projects+='</div></section><section class="section section-ruled" id="ongoing"><div class="container"><div class="section-heading"><div><span class="eyebrow">Ongoing investigations</span><h2>Work in progress'+DOT+'</h2></div><p>Titles carried over from the existing public website. No publication or code-release status is implied.</p></div><div class="work-grid">'
for work in ONGOING['projects']:
    projects+=f'<article class="work-card" id="{work["id"]}"><span class="label">{marker(work["area"])}Ongoing · {E(work["area"])}</span><h3>{E(work["title"])}</h3><p>{E(work["summary"])}</p><p class="authors">{authors(work["authors"])}</p></article>'
projects+='</div><p class="paper-note work-note">† Co-first author · * Corresponding author. Please contact me for discussions about ongoing research.</p></div></section>'
page('projects.html','Projects','NRF-funded research programs and ongoing investigations in graph learning and biomedical AI.',projects)

# 5. About / CV.
cv=intro('About / Curriculum vitae','Sunghong Park<span class="key">.</span>','Researcher in machine learning and biomedical artificial intelligence. Based in Daejeon, Republic of Korea.',aside=f'<div class="intro-mark">{BRAND_MARK}</div>')
cv+=f'<div class="container cv-layout"><aside class="cv-side" aria-label="Researcher profile">{BRAND_MARK}<h2>{E(P["name"])}</h2><p>{E(P["role"])}<br>{E(P["department"])}<br>{E(P["institution_short"])}</p>{external(P["cv_url"],"Download CV (PDF)","btn btn-primary btn-small","download")}<p class="cv-updated small">PDF last updated {E(P["cv_updated"])}.</p><nav class="cv-links" aria-label="CV sections"><a href="#experience">Experience{icon("arrow")}</a><a href="#education">Education{icon("arrow")}</a><a href="#awards">Awards{icon("arrow")}</a><a href="archive.html">Full archive{icon("arrow")}</a></nav></aside><div class="cv-main"><section class="cv-section"><h2>A connected view of learning{DOT}</h2><p>{E(P["biography"])}</p><p class="print-only">{E(P["email"])} · {E(BASE)}</p></section>'
for typ,title in [('experience','Experience'),('education','Education')]:
    cv+=f'<section class="cv-section" id="{typ}"><h2>{title}</h2>'
    for exp in P['experience']:
        if exp['type']!=typ:continue
        current=' is-current' if 'present' in exp['dates'].lower() else ''
        cv+=f'<article class="timeline-entry{current}"><time>{E(exp["dates"])}</time><h3>{E(exp["title"])}</h3><p class="institution">{E(exp["institution"])}</p><p>{E(exp["detail"])}</p></article>'
    cv+='</section>'
cv+='<section class="cv-section" id="awards"><h2>Awards &amp; honors</h2>'
for award in ARCHIVE['awards']:
    cv+=f'<article class="award-row"><time>{award["year"]}</time><div><h3>{E(award["title"])}</h3><p class="award-venue">{E(award["venue"])}</p><p>{E(award["work"])}</p></div></article>'
cv+=f'</section><section class="cv-section"><h2>Research record</h2><p>{len(PUBS)} published journal articles, {len(ARCHIVE["patents"])} patent applications across KR/PCT/US filings, and {len(P["grants"])} NRF research grants as Principal Investigator.</p><p>The full archive preserves the {len(ARCHIVE["conferences"])} individually listed conference records from the public website.</p><div class="btn-group"><a class="btn btn-small" href="archive.html">Browse full archive{icon("arrow")}</a><button type="button" class="btn btn-small js-only" data-print>{icon("print")}Print web CV</button></div></section></div></div>'
page('cv.html','About & CV','Academic background, experience, awards, and curriculum vitae of Sunghong Park at KAIST.',cv)

# 6. Searchable full archive. Patent filings are not represented as grants.
extra=f'<div class="intro-meta archive-summary"><div class="stat"><span class="stat-number">{len(ARCHIVE["patents"])}</span><span class="stat-label">patent applications</span></div><div class="stat"><span class="stat-number">{len(ARCHIVE["conferences"])}</span><span class="stat-label">conference records</span></div><div class="stat"><span class="stat-number">{len(ARCHIVE["awards"])}</span><span class="stat-label">awards</span></div></div>'
archive=intro('Full research archive','A record of<br><span class="key">the work along the way.</span>','Patent applications, conference presentations, and awards. Expand any entry to see its bibliographic or filing details.',extra)
archive+='<div class="container page-content">'
all_years=[int(p['date'][:4]) for p in ARCHIVE['patents']]+[c['year'] for c in ARCHIVE['conferences']]+[a['year'] for a in ARCHIVE['awards']]
archive+=filter_panel([('all','All records'),('patents','Patent applications'),('conferences','Conferences'),('awards','Awards')],all_years,noun='archive records',placeholder='Title, person, application number, or venue',archive=True)
archive+='<div class="record-list">'
for p in ARCHIVE['patents']:
    link=external(p['url'],'View published application') if p.get('url') else ''
    pub=f'<p><strong>Publication:</strong> {E(p["publication"])}</p>' if p.get('publication') else ''
    title_lang=' lang="ko"' if p['jurisdiction']=='KR' else ''
    archive+=f'<details class="archive-item" id="{p["id"]}" data-filter-item data-year="{p["date"][:4]}" data-topics="patents"><summary><span class="archive-kind">{p["jurisdiction"]} filing</span><div class="archive-head"><h2{title_lang}>{E(p["title"])}</h2><p class="archive-meta">{E(p["number"])} · Filed {E(p["date"])}</p></div></summary><div class="archive-detail on-sky"><p><strong>Application number:</strong> {E(p["number"])}</p><p><strong>Inventors:</strong> {E(p["inventors"])}</p>{pub}<p>Application record; no granted-patent status is asserted.</p>{link}</div></details>'
for c in ARCHIVE['conferences']:
    note=f'<p><strong>Source note:</strong> {E(c["note"])}</p>' if c.get('note') else ''
    archive+=f'<details class="archive-item" id="{c["id"]}" data-filter-item data-year="{c["year"]}" data-topics="conferences"><summary><span class="archive-kind">Talk {c["year"]}</span><div class="archive-head"><h2>{E(c["title"])}</h2><p class="archive-meta">{E(c["venue"])}</p></div></summary><div class="archive-detail on-sky"><p><strong>Authors:</strong> {authors(c["authors"])}</p><p><strong>Conference:</strong> {E(c["venue"])}</p>{note}</div></details>'
for i,a in enumerate(ARCHIVE['awards']):
    archive+=f'<details class="archive-item" id="award-{i+1}" data-filter-item data-year="{a["year"]}" data-topics="awards"><summary><span class="archive-kind">Award {a["year"]}</span><div class="archive-head"><h2>{E(a["title"])}</h2><p class="archive-meta">{E(a["venue"])}</p></div></summary><div class="archive-detail on-sky"><p><strong>Recognized work:</strong> {E(a["work"])}</p><p><strong>Authors:</strong> {authors(a["authors"])}</p></div></details>'
archive+='</div><div class="notice">Patent counts refer to individual KR/PCT/US applications, not unique patent families or granted patents. The original homepage summary mentioned 41 conference presentations but individually listed 31; this archive includes only those 31 documented entries.</div></div>'
page('archive.html','Full Archive','Search patent applications, conference presentations, and awards from Sunghong Park’s research archive.',archive)

# 7. A useful server-side 404 fallback (no client-side router required).
broken_edge='<svg class="broken-edge" viewBox="0 0 280 48" aria-hidden="true"><path class="be-line" d="M40 24H140"/><circle class="be-node" cx="24" cy="24" r="14"/><circle class="be-dot" cx="162" cy="24" r="2.5"/><circle class="be-dot" cx="180" cy="24" r="2.5"/><circle class="be-dot" cx="198" cy="24" r="2.5"/><circle class="be-missing" cx="236" cy="24" r="14"/></svg>'
page('404.html','Page not found','The requested page could not be found.',f'<section class="masthead on-ink error-page"><div class="container page-intro">{broken_edge}<span class="eyebrow">404 / A missing connection</span><h1>This path ends here.<br><span class="key">The research continues.</span></h1><p class="lead">The page may have moved during the website redesign. Explore the research archive or return to the homepage.</p><div class="btn-group"><a class="btn btn-primary" href="index.html">Back to home{icon("arrow")}</a><a class="btn" href="publications.html">Find a publication{icon("search")}</a></div></div></section>')

# Infrastructure files. The target domain is opt-in, not an unowned redirect.
(OUT/'.nojekyll').write_text('',encoding='utf-8')
if u.hostname.endswith('.github.io'):
    (OUT/'CNAME').unlink(missing_ok=True)
else:
    if u.path not in ('','/'):
        parser.error('A custom domain must use its root, without a project path.')
    (OUT/'CNAME').write_text(u.hostname+'\n',encoding='utf-8')
(OUT/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n',encoding='utf-8')
urls=''.join(f'<url><loc>{E(BASE+"/"+("" if p=="index.html" else p))}</loc><lastmod>{P["content_reviewed"]}</lastmod></url>' for p in pages)
(OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+urls+'</urlset>',encoding='utf-8')
# Favicon: the brand mark as outlines (Space Grotesk Bold "sp" on an Ink node with a Coral dot),
# so it renders identically without any font.
(OUT/'assets'/'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><circle cx="32" cy="32" r="32" fill="#3A3D44"/><path d="M16.51 41.24Q13.21 41.24 11.1 39.81Q9 38.38 8.55 35.73L12.5 34.71Q12.74 35.9 13.3 36.58Q13.86 37.26 14.69 37.55Q15.52 37.84 16.51 37.84Q18.01 37.84 18.72 37.31Q19.43 36.78 19.43 36Q19.43 35.22 18.75 34.8Q18.07 34.37 16.58 34.1L15.63 33.93Q13.86 33.59 12.4 32.99Q10.93 32.4 10.05 31.34Q9.17 30.29 9.17 28.62Q9.17 26.11 11 24.77Q12.84 23.42 15.83 23.42Q18.65 23.42 20.52 24.68Q22.39 25.94 22.97 27.98L18.99 29.2Q18.72 27.91 17.89 27.37Q17.05 26.82 15.83 26.82Q14.61 26.82 13.96 27.25Q13.31 27.67 13.31 28.42Q13.31 29.24 13.99 29.63Q14.67 30.02 15.83 30.22L16.78 30.39Q18.69 30.73 20.23 31.29Q21.78 31.85 22.68 32.89Q23.58 33.93 23.58 35.7Q23.58 38.35 21.66 39.79Q19.74 41.24 16.51 41.24ZM25.96 47.56V23.9H30.18V25.94H30.79Q31.37 24.95 32.59 24.19Q33.82 23.42 36.09 23.42Q38.13 23.42 39.87 24.42Q41.6 25.43 42.66 27.37Q43.71 29.3 43.71 32.06V32.6Q43.71 35.36 42.66 37.29Q41.6 39.23 39.87 40.23Q38.13 41.24 36.09 41.24Q34.56 41.24 33.53 40.88Q32.49 40.52 31.86 39.96Q31.23 39.4 30.86 38.82H30.25V47.56ZM34.8 37.5Q36.81 37.5 38.12 36.22Q39.43 34.95 39.43 32.5V32.16Q39.43 29.71 38.1 28.44Q36.77 27.16 34.8 27.16Q32.83 27.16 31.5 28.44Q30.18 29.71 30.18 32.16V32.5Q30.18 34.95 31.5 36.22Q32.83 37.5 34.8 37.5Z" fill="#F1F3F4"/><circle cx="52.27" cy="36.16" r="4.6" fill="#FC734D"/></svg>\n',encoding='utf-8')
print(f'Built {len(pages)+1} HTML pages, {len(PUBS)} journal articles, {len(ARCHIVE["patents"])} patent applications, {len(ARCHIVE["conferences"])} conference records.')
print(f'Output: {OUT}\nCanonical site: {BASE}\nCustom-domain CNAME: {"yes" if (OUT/"CNAME").exists() else "no (GitHub Pages first)"}')
