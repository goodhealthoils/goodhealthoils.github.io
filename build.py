#!/usr/bin/env python3
"""Build the Good Health Oils website.

Reads content/*.yml and content/promos/*.yml, renders templates/*.html, and writes the
finished static site to _site/. GitHub Actions runs this on every push (see
.github/workflows/pages.yml). Run locally with:  python3 build.py
"""
import datetime, os, shutil, sys
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
    home_promos = {t: [p for p in promos if p['type'] == t and p.get('show_on_home')] for t in TYPES}

    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(ROOT, 'assets'), os.path.join(OUT, 'assets'))
    for extra in ('CNAME', 'favicon.ico'):
        if os.path.exists(os.path.join(ROOT, extra)): shutil.copy(os.path.join(ROOT, extra), OUT)

    def render(template, url_path, **ctx):
        depth = url_path.strip('/').count('/') + 1 if url_path.strip('/') else 0
        root = '../' * depth
        html = env.get_template(template).render(site=site, root=root, current='/' + url_path.strip('/') + ('/' if url_path.strip('/') else ''),
                                                 year=datetime.date.today().year, **ctx)
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
            render('promo.html', f"promos/{p['slug']}", promo=p, title=p['detail'].get('title'))
        if p.get('banner_options'):
            render('banner-options.html', f"promos/{p['slug']}/banner-options", promo=p, title='Banner options', noindex=True)
    render('promo-archive.html', 'promos', promos=promos, title='All Promotions', noindex=True)
    with open(os.path.join(OUT, '404.html'), 'w', encoding='utf-8') as f:
        f.write(env.get_template('404.html').render(site=site, root='/', current='', year=datetime.date.today().year, title='Page not found'))
    for w in warnings: print('WARNING:', w)
    print(f'Built {sum(len(fs) for _,_,fs in os.walk(OUT))} files into _site/')

if __name__ == '__main__':
    main()
