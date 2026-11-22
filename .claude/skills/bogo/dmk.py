#!/usr/bin/env python3
"""Helper for the /bogo skill: browse and download images from the doTERRA Digital Marketing Kit (Canto, public).

  python3 .claude/skills/bogo/dmk.py folders                 # top-level DMK sections (find "BOGO" here)
  python3 .claude/skills/bogo/dmk.py list FOLDER_ID [WORD]   # every image under a folder, optionally filtered by a word
  python3 .claude/skills/bogo/dmk.py get ASSET_ID OUT.webp [WIDTH]   # download, resize (default 1400px) and save as webp

Needs network access to doterra.canto.com and d3opzdukpbxlns.cloudfront.net, plus Pillow (pip install pillow).
"""
import io, json, sys, urllib.parse, urllib.request

BASE = 'https://doterra.canto.com/rest/v/DigitalMarketingKit'

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=120) as r: return r.read()

def folders():
    for s in json.loads(fetch(f'{BASE}//landing/page/section')):
        if s.get('scheme') in ('folder', 'album'): print(f"{s['path']:8} {s['displayName']}")

def images(folder):
    out, start = [], 0
    while True:
        q = urllib.parse.urlencode({'aggsEnabled': 'false', 'sortBy': 'name', 'sortDirection': 'true', 'size': 100,
                                    'start': start, 'operator': 'and', 'scheme': 'image'})
        hits = json.loads(fetch(f'{BASE}/search/folder/{folder}?{q}'))['hits']
        out += [h for h in hits['hit'] if h['scheme'] == 'image']
        start += 100
        if start >= hits['found']: return out

def list_images(folder, word=''):
    seen = set()
    for h in sorted(images(folder), key=lambda h: h['displayName']):
        n = h['displayName']
        if n in seen or word.lower() not in n.lower(): continue
        seen.add(n); d = h['data']
        print(f"{h['path']}  {d.get('width', ['?'])[0]}x{d.get('height', ['?'])[0]}  {n}")

def get(asset, dest, width=1400):
    from PIL import Image
    img = Image.open(io.BytesIO(fetch(f'{BASE}/binary/advance/image/{asset}/download'))).convert('RGB')
    if img.width > width: img = img.resize((width, round(img.height * width / img.width)), Image.LANCZOS)
    img.save(dest, 'WEBP', quality=86)
    print(f'saved {dest} {img.width}x{img.height}')

if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['folders']: folders()
    elif a[:1] == ['list']: list_images(a[1], a[2] if len(a) > 2 else '')
    elif a[:1] == ['get']: get(a[1], a[2], int(a[3]) if len(a) > 3 else 1400)
    else: print(__doc__)
