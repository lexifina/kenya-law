"""Give the FAOLEX / WIPO Lex PDFs that build.py held for want of a day to web_build.py's commencement reader
(section 1 "on publication" / "on assent" / Gazette Supplement date). Appends to nat_cands.json."""
import hashlib, json, shutil, urllib.parse
from pathlib import Path
W = Path(r'kenya-law-work')
held = json.loads((W / 'held.json').read_text('utf-8'))
n = json.loads((W / 'nat_cands.json').read_text())
have = {x['url'] for x in n}
meta = {}
for p in (W / 'cache' / 'faolex' / 'meta').glob('*.json'):
    d = json.loads(p.read_text('utf-8'))
    for f in d.get('links_to_full_text') or []:
        meta['https://faolex.fao.org/docs/pdf/' + f] = (d.get('title_of_text') or '', d['_url'], W / 'cache' / 'faolex' / 'pdf' / f)
for p in (W / 'cache' / 'wipo').glob('*.json'):
    d = json.loads(p.read_text('utf-8'))
    for x in d.get('pdfs', []):
        meta[x['url']] = (d.get('title', ''), d['url'], W / 'cache' / 'wipo' / x['name'])
add = 0
for u, why in held.items():
    if not why.startswith(('no day of commencement', 'commencement by notice')) or u in have or u not in meta:
        continue
    title, rec, src = meta[u]
    if not src.exists():
        continue
    q = W / 'cache' / 'web' / (hashlib.sha1(u.encode()).hexdigest() + '.pdf')
    if not q.exists():
        shutil.copy(src, q)
    n.append({'county': None, 'host': u.split('/')[2], 'title': title, 'url': u, 'wpdate': None,
              'secondary': 'FAOLEX (FAO)' if 'faolex' in u else 'WIPO Lex (WIPO)', 'record': rec})
    add += 1
(W / 'nat_cands.json').write_text(json.dumps(n, indent=0))
print('added', add, len(n))
