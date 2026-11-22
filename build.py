#!/usr/bin/env python3
"""Build the Good Health Oils website.

Reads content/*.yml and content/promos/*.yml, renders templates/*.html, and writes the
finished static site to _site/. GitHub Actions runs this on every push (see
.github/workflows/pages.yml). Run locally with:  python3 build.py
"""
import datetime, hashlib, os, shutil, sys
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, '_site')
TYPES = ('monthly', 'seasonal', 'bogo')
warnings = []

def load(path):
    with open(os.path.join(ROOT, 'content', path), encoding='utf-8') as f:
        return yaml.safe_load(f) or {}

def as_date(v):
    if v in (None, ''): return None
    if isinstance(v, datetime.date): return v
    return datetime.date.fromisoformat(str(v))

def check_image(path, where):
    if path and not path.startswith('http') and not os.path.exists(os.path.join(ROOT, path)):
        warnings.append(f'missing image {path} ({where})')

def load_promos():
    promos = []
    folder = os.path.join(ROOT, 'content', 'promos')
    for name in sorted(os.listdir(folder)):
        if not name.endswith(('.yml', '.yaml')): continue
        p = load(os.path.join('promos', name))
        p.setdefault('slug', name.rsplit('.', 1)[0])
        if p.get('type') not in TYPES:
            sys.exit(f'{name}: type must be one of {TYPES}')
        p['start'], p['end'] = as_date(p.get('start')), as_date(p.get('end'))
        # BOGO only: show_from / show_until are when the page and home picture appear and disappear
        # (start/end are the sale days). Everything else uses start/end for both.
        p['show_from'], p['show_until'] = as_date(p.get('show_from')), as_date(p.get('show_until'))
        p['home_start'], p['home_end'] = p['show_from'] or p['start'], p['show_until'] or p['end']
        p['soon_until'] = p['start'] - datetime.timedelta(days=1) if p['start'] else None   # last "coming" day
        p['has_page'] = bool(p.get('detail'))
        for it in (p.get('items') or []) + ((p.get('detail') or {}).get('items') or []):
            check_image(it.get('image'), name)
        for key in ('banner', 'home_card'):
            if p.get(key): check_image(p[key].get('image'), name)
        promos.append(p)
    return promos

def main():
    site = load('site.yml')
    env = Environment(loader=FileSystemLoader(os.path.join(ROOT, 'templates')),
                      autoescape=select_autoescape(['html']), trim_blocks=True, lstrip_blocks=True)
    promos = load_promos()
    # The BOGO turned on with show_on_home also lives at the fixed address /bogo/ (dates decide when it shows).
    live_bogos = [p for p in promos if p['type'] == 'bogo' and p.get('show_on_home') and p['has_page']]
    current_bogo = max(live_bogos, key=lambda p: p['start'] or datetime.date.min) if live_bogos else None
    for p in promos: p['page_path'] = 'bogo' if p is current_bogo else f"promos/{p['slug']}"
    env.globals['current_bogo'] = current_bogo   # for the "BOGO's are LIVE" banner under the menu
    home_promos = {t: [p for p in promos if p['type'] == t and p.get('show_on_home')] for t in TYPES}

    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(ROOT, 'assets'), os.path.join(OUT, 'assets'))
    for extra in ('CNAME', 'favicon.ico'):
        if os.path.exists(os.path.join(ROOT, extra)): shutil.copy(os.path.join(ROOT, extra), OUT)

    # version tag on the stylesheet so phones and browsers pick up CSS changes right away
    with open(os.path.join(ROOT, 'assets', 'css', 'site.css'), 'rb') as f: css_v = hashlib.md5(f.read()).hexdigest()[:8]

    def render(template, url_path, **ctx):
        depth = url_path.strip('/').count('/') + 1 if url_path.strip('/') else 0
        root = '../' * depth
        html = env.get_template(template).render(site=site, root=root, current='/' + url_path.strip('/') + ('/' if url_path.strip('/') else ''),
                                                 year=datetime.date.today().year, css_v=css_v, **ctx)
        dest = os.path.join(OUT, url_path.strip('/'), 'index.html')
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, 'w', encoding='utf-8') as f: f.write(html)

    render('index.html', '', page=load('home.yml'), promos=home_promos, title=None)
    render('about.html', 'about', page=load('about.yml'), title='About')
    render('how-to-use.html', 'how-to-use', page=load('how-to-use.yml'), title='How To Use')
    render('newsletter.html', 'newsletter', page=load('newsletter.yml'), title='Newsletter')
    render('learn.html', 'learn', page=load('learn.yml'), title='Learn')
    render('shop.html', 'shop', page=load('shop.yml'), title='Shop')
    render('reset.html', '90-day-reset', page=load('90-day-reset.yml'), title='90 Day Reset')
    for p in promos:
        if p['has_page']:
            # every promo keeps a preview/archive copy here (the BOGO copy is not date-gated, so keep it out of search)
            render('promo.html', f"promos/{p['slug']}", promo=p, title=p['detail'].get('title'), noindex=p['type'] == 'bogo')
        if p.get('banner_options'):
            render('banner-options.html', f"promos/{p['slug']}/banner-options", promo=p, title='Banner options', noindex=True)
    render('bogo.html', 'bogo', promo=current_bogo, title='BOGO Week')
    render('promo-archive.html', 'promos', promos=promos, title='All Promotions', noindex=True)
    with open(os.path.join(OUT, '404.html'), 'w', encoding='utf-8') as f:
        f.write(env.get_template('404.html').render(site=site, root='/', current='', year=datetime.date.today().year, title='Page not found'))
    for w in warnings: print('WARNING:', w)
    print(f'Built {sum(len(fs) for _,_,fs in os.walk(OUT))} files into _site/')

if __name__ == '__main__':
    main()
