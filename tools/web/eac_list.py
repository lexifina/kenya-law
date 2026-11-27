import re, json, html, requests, urllib3
from pathlib import Path
urllib3.disable_warnings()
W = Path(r'kenya-law-work')
r = requests.get('https://www.eala.org/documents/category/acts-of-the-community',
                 headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0'}, timeout=60)
seen = {}
for u, t in re.findall(r'href="(https://www.eala.org/uploads/[^"]+\.pdf)"[^>]*>(.*?)</a>', r.text, re.S | re.I):
    t = html.unescape(re.sub(r'<[^>]+>|\s+', ' ', t)).strip()
    if t and u not in seen:
        seen[u] = t
n = json.loads((W / 'nat_cands.json').read_text())
have = {x['url'] for x in n}
for u, t in seen.items():
    if u not in have:
        n.append({'county': None, 'host': 'www.eala.org', 'title': t, 'url': u, 'wpdate': None, 'region': 'eac'})
(W / 'nat_cands.json').write_text(json.dumps(n, indent=0))
print(len(seen), len(n))
