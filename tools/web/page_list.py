"""Collect PDF links from listing pages of ministry/regulator sites (Drupal-style ?page=N) into nat_cands.json."""
import html, json, re, time, urllib.parse, requests, urllib3
from pathlib import Path
urllib3.disable_warnings()
W = Path(r'kenya-law-work')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36'}
PAGES = ['https://www.treasury.go.ke/acts', 'https://www.treasury.go.ke/legal-and-gazette-notice',
         'https://www.treasury.go.ke/legal-documents', 'https://www.epra.go.ke/regulations', 'https://www.epra.go.ke/acts',
         'https://www.epra.go.ke/legislation']
NEG = re.compile(r'\bbill|draft|report|policy|strategy|guideline|form\b|framework|plan\b|tender|budget|circular|'
                 r'presentation|values|principles|designation|viability|net-metering|memorandum|statement', re.I)
n = json.loads((W / 'nat_cands.json').read_text())
have = {x['url'] for x in n}
add = 0
for base in PAGES:
    for page in range(0, 40):
        try:
            r = requests.get(base, params={'page': page} if page else None, headers=UA, timeout=(15, 60), verify=False)
        except Exception as e:  # noqa: BLE001
            print(base, page, type(e).__name__)
            break
        if r.status_code != 200:
            break
        links = re.findall(r'href="([^"]+\.pdf)"[^>]*>(.*?)</a>', r.text, re.S | re.I)
        new = 0
        for u, t in links:
            u = urllib.parse.urljoin(r.url, html.unescape(u))
            t = html.unescape(re.sub(r'<[^>]+>|\s+', ' ', t)).strip()
            fn = urllib.parse.unquote(u.rsplit('/', 1)[-1])
            if t.lower() in ('download', 'view', ''):
                t = fn
            if NEG.search(t + ' ' + fn) or u in have:
                continue
            have.add(u)
            n.append({'county': None, 'host': u.split('/')[2], 'title': t, 'url': u, 'wpdate': None})
            new += 1
            add += 1
        print(base, page, len(links), new, flush=True)
        time.sleep(1)
        if not new:
            break
(W / 'nat_cands.json').write_text(json.dumps(n, indent=0))
print('added', add, 'total', len(n))
