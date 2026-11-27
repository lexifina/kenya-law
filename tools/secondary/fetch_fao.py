"""FAOLEX Kenya: record metadata (prerendered JSON on each record page) then the full-text PDFs of legal texts.
python -I fetch_fao.py   (detached; logs to ../progress.log; STOP file in ../ stops it)"""
import json, re, time, threading, hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import requests
W = Path(r'kenya-law-work')
META = W / 'cache' / 'faolex' / 'meta'; PDF = W / 'cache' / 'faolex' / 'pdf'
META.mkdir(parents=True, exist_ok=True); PDF.mkdir(parents=True, exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36'}
tl = threading.local(); lock = threading.Lock(); state = {'bad': 0, 'last': 0.0}
GAP = 0.6
def log(m):
    with lock, open(W / 'progress.log', 'a', encoding='utf-8') as f: f.write(time.strftime('%H:%M:%S ') + 'fao: ' + m + '\n')
def get(u):
    for a in range(4):
        if (W / 'STOP').exists(): raise SystemExit
        with lock:
            w = state['last'] + GAP - time.time()
            state['last'] = max(time.time(), state['last'] + GAP)
        if w > 0: time.sleep(w)
        try:
            s = getattr(tl, 's', None) or requests.Session(); tl.s = s
            r = s.get(u, headers=UA, timeout=(20, 120))
        except Exception as e:
            log(f'err {type(e).__name__} {u[-30:]}'); tl.s = None; time.sleep(5 * (a + 1)); continue
        if r.status_code in (429, 403, 503):
            state['bad'] += 1; log(f'{r.status_code} {u}; backing off'); time.sleep(60 * (a + 1))
            if state['bad'] > 5: log('too many refusals: stopping'); raise SystemExit
            continue
        return r
    return None
def meta(u):
    fid = re.search(r'(LEX-FAOC\d+)', u).group(1)
    p = META / f'{fid}.json'
    if p.exists(): return
    r = get(u)
    if r is None or r.status_code != 200: log(f'meta {r and r.status_code} {u}'); return
    m = re.search(r'id="prerendered-document">(.*?)</script>', r.text, re.S)
    if not m: log(f'no json {u}'); return
    d = json.loads(m.group(1))['doc']; d['_url'] = u
    p.write_text(json.dumps(d, ensure_ascii=False), 'utf-8')
SKIP_TYPES = {'Policy', 'Miscellaneous'}
def pdf(name):
    p = PDF / name
    if p.exists(): return
    r = get('https://faolex.fao.org/docs/pdf/' + name)
    if r is None or r.status_code != 200 or not r.content.startswith(b'%PDF'):
        log(f'pdf {r and r.status_code} {name}'); (PDF / (name + '.missing')).write_text(str(r and r.status_code)); return
    tmp = p.with_suffix('.part'); tmp.write_bytes(r.content); tmp.replace(p)
def main():
    L = json.loads((W / 'faolex_ken.json').read_text())
    log(f'meta: {len(L)} records')
    with ThreadPoolExecutor(2) as ex: list(ex.map(meta, L))
    names = []
    for p in META.glob('*.json'):
        d = json.loads(p.read_text('utf-8'))
        types = {t['name'] for t in d.get('type_of_text') or []}
        if types and types <= SKIP_TYPES: continue
        for n in d.get('links_to_full_text') or []:
            if n.lower().endswith('.pdf') and not (PDF / (n + '.missing')).exists(): names.append(n)
    log(f'meta done; {len(names)} pdfs to fetch')
    done = 0
    with ThreadPoolExecutor(2) as ex:
        for _ in ex.map(pdf, names):
            done += 1
            if done % 100 == 0: log(f'pdf {done}/{len(names)}')
    log('DONE')
if __name__ == '__main__':
    main()

