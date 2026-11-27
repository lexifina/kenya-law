"""List every PDF in the WordPress media libraries of Kenya's county assembly / county government sites.
Writes cache/county/list/<host>.json. One request at a time per host, 1 s apart."""
import json, time, requests, urllib3, concurrent.futures as cf
from pathlib import Path
urllib3.disable_warnings()
W = Path(r'kenya-law-work')
OUT = W / 'cache' / 'county' / 'list'
OUT.mkdir(parents=True, exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36'}


def log(m):
    with open(W / 'progress.log', 'a', encoding='utf-8') as f:
        f.write(time.strftime('%H:%M:%S ') + 'nlist: ' + m + '\n')


def run(host):
    p = OUT / f'{host}.json'
    if p.exists():
        return
    items, page = [], 1
    while True:
        for a in range(3):
            try:
                r = requests.get(f'https://{host}/wp-json/wp/v2/media', headers=UA, timeout=(15, 90), verify=False,
                                 params={'mime_type': 'application/pdf', 'per_page': 100, 'page': page,
                                         '_fields': 'id,date,title,source_url,slug'})
                break
            except Exception as e:  # noqa: BLE001
                log(f'{host} p{page} retry {a} {type(e).__name__}')
                time.sleep(10)
        else:
            log(f'{host} gave up at page {page}')
            break
        if r.status_code in (403, 429):
            log(f'{host} {r.status_code}: stop host')
            break
        if r.status_code != 200:
            break
        d = r.json()
        if not d:
            break
        items += [{'id': x['id'], 'date': x['date'], 'title': x['title']['rendered'], 'url': x['source_url']} for x in d]
        tp = int(r.headers.get('X-WP-TotalPages') or 1)
        if page >= tp:
            break
        page += 1
        time.sleep(1)
    p.write_text(json.dumps(items, indent=0), 'utf-8')
    log(f'{host}: {len(items)} pdfs')


pr = json.loads((W / 'nat_probe.json').read_text())
hosts = [h for h, (st, tot) in pr.items() if st == 200 and tot and int(tot) > 5]
log(f'{len(hosts)} hosts')
with cf.ThreadPoolExecutor(10) as ex:
    list(ex.map(run, hosts))
log('DONE')
