"""WIPO Lex Kenya: every legislation record (results list, all versions) -> meta json + main-text PDFs."""
import json, re, time, html
from pathlib import Path
import requests
W = Path(r'C:\Users\alany\Documents\kenya-law-work')
D = W / 'cache' / 'wipo'; D.mkdir(parents=True, exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36'}
def log(m):
    with open(W / 'progress.log', 'a', encoding='utf-8') as f: f.write(time.strftime('%H:%M:%S ') + 'wipo: ' + m + '\n')
def get(u):
    time.sleep(1.0)
    if (W / 'STOP').exists(): raise SystemExit
    for a in range(5):
        try:
            r = requests.get(u, headers=UA, timeout=120); break
        except requests.RequestException as e:
            log(f'retry {a} {type(e).__name__} {u[:90]}'); time.sleep(20 * (a + 1))
    else:
        return None
    if r.status_code in (403, 429): log(f'{r.status_code} {u}: stopping'); raise SystemExit
    return r
def text(h):
    t = re.sub(r'<script.*?</script>|<style.*?</style>|<nav.*?</nav>|<header.*?</header>|<footer.*?</footer>', '', h, flags=re.S)
    s = html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' | ', t)))
    return re.sub(r'(\|\s*)+', '| ', s)
def main():
    r = get('https://www.wipo.int/wipolex/en/legislation/results?countryOrgs=KE&last=false')
    ids = sorted(set(re.findall(r'/wipolex/en/legislation/details/(\d+)', r.text)), key=int)
    log(f'{len(ids)} records')
    for i in ids:
        mp = D / f'{i}.json'
        if mp.exists(): continue
        r = get(f'https://www.wipo.int/wipolex/en/legislation/details/{i}')
        if r is None or r.status_code != 200: log(f'skip {i}'); continue
        s = text(r.text)
        m = re.search(r'<title>(.*?)</title>', r.text, re.S)
        d = {'id': i, 'title': html.unescape(m.group(1)).strip() if m else '', 'url': f'https://www.wipo.int/wipolex/en/legislation/details/{i}'}
        for k in ['Year of Version', 'Amended up to:', 'Commenced:', 'Assented:', 'Enacted:', 'Adopted:', 'Entry into force:', 'Published:', 'Type of Text', 'WIPO Lex No.']:
            mm = re.search(re.escape(k) + r' \| ([^|]+)\|', s)
            if mm: d[k.rstrip(':')] = mm.group(1).strip()
        mt = re.search(r'Main text\(s\) \| Main text\(s\) \| (.*?)(?:Related text|WIPO Lex No\.)', s)
        d['main'] = mt.group(1)[:500] if mt else ''
        pdfs = [html.unescape(u) for u in re.findall(r'href="(https://wipolex-res\.wipo\.int/edocs/lexdocs/laws/[^"]+?\.pdf[^"]*)"', r.text)]
        d['pdfs'] = []
        for u in dict.fromkeys(pdfs):
            name = u.split('?')[0].rsplit('/', 1)[1]
            p = D / name
            if not p.exists():
                rr = get(u)
                if rr is not None and rr.status_code == 200 and rr.content.startswith(b'%PDF'): p.write_bytes(rr.content)
                else: log(f'pdf failed {name}'); continue
            d['pdfs'].append({'name': name, 'url': 'https://wipolex-res.wipo.int/edocs/lexdocs/laws/' + u.split('/lexdocs/laws/')[1].split('?')[0]})
        mp.write_text(json.dumps(d, ensure_ascii=False, indent=1), 'utf-8')
    log('DONE')
main()

