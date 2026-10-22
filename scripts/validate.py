#!/usr/bin/env python3
"""Offline validation of generated pages. No network access or dependencies.
Checks local file links, anchors, duplicate IDs, h1s, metadata, structured data,
reference counts, expected assets, and publication identifiers.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--site',default=str(Path(__file__).resolve().parents[1]/'site'))
args=parser.parse_args()
root=Path(args.site).resolve()

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids=[]; self.refs=[]; self.h1s=0; self.lang=None
        self.canonical=None; self.description=False; self.title=False
        self.json_data=[]; self.in_json=False; self.json_buffer=''
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        if tag=='h1':self.h1s+=1
        if tag=='html':self.lang=a.get('lang')
        if tag=='title':self.title=True
        if tag=='meta' and a.get('name')=='description': self.description=bool(a.get('content'))
        if tag=='link' and a.get('rel')=='canonical':self.canonical=a.get('href')
        if tag in ['a','link'] and a.get('href'):self.refs.append(a['href'])
        if tag in ['img','script'] and a.get('src'):self.refs.append(a['src'])
        if tag=='meta' and a.get('property')=='og:image':
            self.refs.append('assets/'+a['content'].split('/assets/')[-1])
        if tag=='script' and a.get('type')=='application/ld+json': self.in_json=True;self.json_buffer=''
    def handle_data(self,data):
        if self.in_json:self.json_buffer+=data
    def handle_endtag(self,tag):
        if tag=='script' and self.in_json:
            self.json_data.append(self.json_buffer);self.in_json=False

errors=[]; count=0; parsed={}
for path in root.glob('*.html'):
    p=PageParser();p.feed(path.read_text(encoding='utf-8'));parsed[path.name]=p
for filename,p in parsed.items():
    if p.h1s!=1:errors.append(f'{filename}: expected 1 h1, got {p.h1s}')
    if not all([p.lang,p.title,p.description,p.canonical]):errors.append(f'{filename}: missing document metadata')
    for value,n in Counter(p.ids).items():
        if n>1:errors.append(f'{filename}: duplicate ID {value}')
    for value in p.json_data:
        try:json.loads(value)
        except json.JSONDecodeError as e:errors.append(f'{filename}: invalid JSON-LD: {e}')
    for ref in p.refs:
        url=urlparse(ref)
        if url.scheme or url.netloc:
            if url.scheme not in ['https','mailto','tel','data']:errors.append(f'{filename}: unsafe/unsupported URL scheme {ref}')
            continue
        name=unquote(url.path) or filename
        target=(root/name).resolve()
        if not target.is_relative_to(root):errors.append(f'{filename}: link escapes site: {ref}');continue
        if not target.exists():errors.append(f'{filename}: missing file {ref}')
        if url.fragment and name in parsed and unquote(url.fragment) not in parsed[name].ids:
            errors.append(f'{filename}: missing anchor {ref}')
        count+=1
for expected in ['index.html','research.html','publications.html','projects.html','cv.html','archive.html','404.html','.nojekyll','robots.txt','sitemap.xml','publications.bib','assets/styles.css','assets/site.js','assets/theme.js','assets/site-data.js','assets/og-card.png','assets/favicon.svg']:
    if not (root/expected).is_file():errors.append(f'Missing expected file: {expected}')
profile=json.loads((root.parent/'content/profile.json').read_text()) if (root.parent/'content/profile.json').exists() else None
if profile:
    pubs=json.loads((root.parent/'content/publications.json').read_text())
    for p in pubs:
        if p['id'] not in parsed['publications.html'].ids:errors.append(f'Missing publication: {p["id"]}')
    if (root/'publications.bib').read_text().count('@article{')!=len(pubs):errors.append('BibTeX count differs from published article count')
if errors:
    print('\n'.join('ERROR: '+e for e in errors))
    raise SystemExit(1)
print(f'PASS: {len(parsed)} HTML pages; {count} local link/asset references; unique IDs; valid local anchors; metadata; JSON-LD; required assets; bibliography.')
print('External URLs, domain ownership, DNS, certificates and remote deployment are not checked by this offline validator.')
