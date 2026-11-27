"""Download the candidate PDFs (county_cands.json, nat_cands.json) to cache/web/<sha1(url)>.pdf.
One request at a time per host, 1 s apart; hosts in parallel. A 403/429 stops that host."""
import hashlib, json, time, requests, urllib3, collections, concurrent.futures as cf
from pathlib import Path
urllib3.disable_warnings()
W = Path(r'kenya-law-work')
D = W / 'cache' / 'web'
D.mkdir(parents=True, exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36'}


def log(m):
    with open(W / 'progress.log', 'a', encoding='utf-8') as f:
        f.write(time.strftime('%H:%M:%S ') + 'wfetch: ' + m + '\n')


def path(u):
    return D / (hashlib.sha1(u.encode()).hexdigest() + '.pdf')


def run(host, urls):
    n = 0
    for u in urls:
        if (W / 'STOP').exists():
            return
        p = path(u)
        if p.exists() or p.with_suffix('.bad').exists():
            continue
        for a in range(3):
            try:
                r = requests.get(u, headers=UA, timeout=(15, 180), verify=False)
                break
            except Exception as e:  # noqa: BLE001
                log(f'{host} retry {a} {type(e).__name__}')
                time.sleep(10)
        else:
            continue
        time.sleep(1)
        if r.status_code in (403, 429):
            log(f'{host} {r.status_code}: stop host')
            STOPPED.add(host)
            return
        if r.status_code == 200 and r.content[:5] == b'%PDF-':
            p.write_bytes(r.content)
            n += 1
        else:
            p.with_suffix('.bad').write_text(str(r.status_code))
    log(f'{host}: {n} new')


STOPPED = set()
for _pass in range(3):
    by = collections.defaultdict(list)
    for f in ('county_cands.json', 'nat_cands.json', 'crawl_cands.json'):
        if (W / f).exists():
            for x in json.loads((W / f).read_text('utf-8')):
                by[x['url'].split('/')[2]].append(x['url'])
    todo = {h: [u for u in us if not path(u).exists() and not path(u).with_suffix('.bad').exists()] for h, us in by.items()}
    todo = {h: us for h, us in todo.items() if us and h not in STOPPED}
    if not todo:
        break
    log(f'{sum(map(len, todo.values()))} to fetch on {len(todo)} hosts')
    with cf.ThreadPoolExecutor(16) as ex:
        list(ex.map(lambda kv: run(*kv), todo.items()))
    if (W / 'STOP').exists():
        break
log('DONE')
