#!/usr/bin/env python3
"""Optional Chromium UI checks; not a build/runtime dependency.
Install for local testing: pip install playwright && playwright install chromium
Run: python scripts/browser_smoke.py
Use --inline only in environments that disallow HTTP/file navigation. It embeds
unchanged CSS/JS into the generated HTML, so it tests rendering/interactions but
not resource loading or actual navigation.
"""
from pathlib import Path
import argparse
import functools
import http.server
import json
import shutil
import threading
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--inline',action='store_true')
parser.add_argument('--screenshots',action='store_true')
args=parser.parse_args()
results=[];errors=[];server=None

def embedded(name):
    text=(SITE/name).read_text(encoding='utf-8')
    text=text.replace('<link rel="stylesheet" href="assets/styles.css">','<style>'+(SITE/'assets/styles.css').read_text(encoding='utf-8')+'</style>')
    text=text.replace('<script src="assets/theme.js"></script>','<script>'+(SITE/'assets/theme.js').read_text(encoding='utf-8')+'</script>')
    scripts=''
    for script in ['site-data.js','site.js']:
        text=text.replace(f'<script src="assets/{script}" defer></script>','')
        scripts+='<script>'+(SITE/'assets'/script).read_text(encoding='utf-8')+'</script>'
    return text.replace('</body>',scripts+'</body>')

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*_): pass

if not args.inline:
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(SITE)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    origin=f'http://127.0.0.1:{server.server_address[1]}'

def load(page,name):
    page.on('pageerror',lambda error:errors.append(str(error)))
    if args.inline:page.set_content(embedded(name),wait_until='load')
    else:page.goto(origin+'/'+name,wait_until='networkidle')

def check(label,condition):
    if not condition:raise AssertionError(label)
    results.append(label)

try:
    with sync_playwright() as p:
        executable=shutil.which('chromium') or shutil.which('chromium-browser')
        kwargs={'headless':True}
        if executable:kwargs['executable_path']=executable
        browser=p.chromium.launch(**kwargs)
        names=['index.html','research.html','publications.html','projects.html','cv.html','archive.html','404.html']
        for width in [320,390,768,1024,1440]:
            for name in names:
                page=browser.new_page(viewport={'width':width,'height':900})
                load(page,name)
                check(f'{name} / {width}px: no horizontal overflow',page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'))
                check(f'{name} / {width}px: one main heading',page.locator('h1').count()==1)
                page.close()
        page=browser.new_page(viewport={'width':1440,'height':1000})
        load(page,'publications.html')
        visible=lambda:page.locator('[data-filter-item]:visible').count()
        check('Publications: 13 articles initially',visible()==13)
        page.locator('[data-search]').fill('NeuroFANN')
        check('Publication text search',visible()==1)
        page.locator('#year-filter').select_option('2024')
        check('Combined search + year / empty state',visible()==0 and page.locator('[data-empty]').is_visible())
        page.locator('[data-reset]').click()
        check('Reset restores all publications',visible()==13)
        page.locator('[data-filter="Biomedical AI"]').click()
        check('Research direction filter',visible()==10)
        page.locator('[data-reset]').click()
        page.locator('[data-cite="neurofann-2025"]').click()
        check('Citation dialog opens',page.locator('dialog').is_visible())
        page.locator('[data-citation-format="bibtex"]').click()
        check('BibTeX includes verified NeuroFANN DOI','10.1093/bib/bbaf366' in page.locator('#citation-text').input_value())
        page.locator('[data-copy-citation]').click()
        check('Citation copy feedback', any(text in page.locator('#citation-feedback').inner_text() for text in ['copied.', 'Text selected.']))
        page.keyboard.press('Escape')
        check('Escape closes citation dialog',not page.locator('dialog').is_visible())
        check('Citation dialog restores focus',page.locator('[data-cite="neurofann-2025"]').evaluate('(e)=>e===document.activeElement'))
        page.close()
        page=browser.new_page(viewport={'width':390,'height':844})
        load(page,'index.html')
        menu=page.locator('[data-menu-toggle]')
        menu.click()
        check('Mobile navigation expands',menu.get_attribute('aria-expanded')=='true' and page.locator('#main-navigation').is_visible())
        check('Contact available in mobile menu',page.locator('.mobile-contact-link').is_visible())
        page.keyboard.press('Escape')
        check('Mobile navigation closes on Escape',menu.get_attribute('aria-expanded')=='false')
        page.locator('[data-theme-toggle]').click()
        check('Dark theme toggle',page.locator('html').get_attribute('data-theme')=='dark')
        page.locator('[data-theme-toggle]').click()
        check('Light theme toggle',page.locator('html').get_attribute('data-theme')=='light')
        page.locator('[data-map-mode="adaptation"]').click()
        check('Conceptual map mode switch',page.locator('#research-map-svg').get_attribute('data-mode')=='adaptation')
        page.locator('[data-copy-email]').click()
        check('Email copy feedback',page.locator('#toast').is_visible())
        page.close()
        page=browser.new_page(viewport={'width':1440,'height':1000})
        load(page,'archive.html')
        check('Archive initial record count',page.locator('[data-filter-item]:visible').count()==52)
        page.locator('[data-filter="patents"]').click()
        check('Patent application filter',page.locator('[data-filter-item]:visible').count()==17)
        page.locator('[data-search]').fill('PCT')
        check('Archive keyword search',page.locator('[data-filter-item]:visible').count()==3)
        page.locator('[data-reset]').click()
        page.locator('[data-filter="conferences"]').click()
        check('Conference filter',page.locator('[data-filter-item]:visible').count()==31)
        page.locator('[data-filter-item]:visible').first.locator('summary').click()
        check('Archive entry expands',page.locator('[data-filter-item]:visible').first.get_attribute('open') is not None)
        page.close()
        context=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
        page=context.new_page();load(page,'publications.html')
        check('Without JavaScript: all publication content remains',page.locator('.pub-item').count()==13)
        check('Without JavaScript: navigation remains available',page.locator('#main-navigation').is_visible())
        check('Without JavaScript: no horizontal overflow',page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'))
        context.close()
        context=browser.new_context(reduced_motion='reduce',viewport={'width':1440,'height':1000})
        page=context.new_page();load(page,'index.html')
        check('Reduced motion disables smooth scrolling',page.evaluate('getComputedStyle(document.documentElement).scrollBehavior')=='auto')
        check('Desktop hides hamburger control',not page.locator('[data-menu-toggle]').is_visible())
        page.locator('[data-theme-toggle]').click()
        if args.screenshots:
            (ROOT/'previews').mkdir(exist_ok=True)
            page.screenshot(path=str(ROOT/'previews/dark-mode.png'),full_page=True)
        context.close()
        check('No JavaScript runtime exceptions',not errors)
        browser.close()
finally:
    if server:server.shutdown()
report={'status':'passed','checks':len(results),'mode':'inline-rendering' if args.inline else 'local-http','results':results,'javascript_errors':errors,'limitations':['No remote GitHub Actions deployment was executed.','External links and the linked CV PDF were not exhaustively verified.','DNS, domain ownership and HTTPS certificates are not tested.','Inline mode does not test real navigation/resource fetching or localStorage persistence.']}
(ROOT/'docs/browser-test-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'passed','checks':len(results),'mode':report['mode'],'javascript_errors':errors}))
