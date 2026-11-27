"""Shallow crawl of county sites without a WordPress media API: home page -> pages whose link text/URL says
legislation / acts / laws / gazette / regulations / downloads (2 levels) -> PDF links that look like legislation.
1 s between requests per host; a 403/429 stops the host. Appends to county_cands.json."""
import html, json, re, sys, time, urllib.parse, requests, urllib3, concurrent.futures as cf
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
urllib3.disable_warnings()
W = Path(r'kenya-law-work')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36'}
HOSTS = ('kilifi.go.ke taitataveta.go.ke isiolo.go.ke nyandarua.go.ke kitui.go.ke kituiassembly.go.ke mombasa.go.ke '
         'mombasaassembly.go.ke kiambu.go.ke kiambuassembly.go.ke nairobiassembly.go.ke nairobi.go.ke kisii.go.ke '
         'transnzoia.go.ke transnzoiaassembly.go.ke uasingishu.go.ke kericho.go.ke baringo.go.ke baringoassembly.go.ke '
         'vihiga.go.ke nyamira.go.ke nyamiraassembly.go.ke homabay.go.ke migori.go.ke tharakanithiassembly.go.ke '
         'kisumuassembly.go.ke turkanaassembly.go.ke manderaassembly.go.ke embu.go.ke laikipiaassembly.go.ke '
         'makueniassembly.go.ke samburuassembly.go.ke kirinyagaassembly.go.ke nyeriassembly.go.ke bometassembly.go.ke '
         'kerichoassembly.go.ke kajiadoassembly.go.ke narokassembly.go.ke westpokotassembly.go.ke kwaleassembly.go.ke '
         'siaya.go.ke busia.go.ke busiaassembly.go.ke nandiassembly.go.ke kakamegaassembly.go.ke bungomaassembly.go.ke '
         'uasingishuassembly.go.ke elgeyomarakwetassembly.go.ke garissa.go.ke wajirassembly.go.ke marsabit.go.ke').split()
NAV = re.compile(r'legislat|\bacts?\b|/acts?\b|laws?\b|gazette|regulation|downloads?|documents?|publications?|resources|'
                 r'bills-and-acts|county-acts|policies-and-legislation', re.I)
from county_pick import POS, NEG, COUNTY  # noqa: E402


def log(m):
    with open(W / 'progress.log', 'a', encoding='utf-8') as f:
        f.write(time.strftime('%H:%M:%S ') + 'crawl: ' + m + '\n')


def get(s, u):
    try:
        r = s.get(u, headers=UA, timeout=(15, 60), verify=False)
        time.sleep(1)
        return r
    except Exception:  # noqa: BLE001
        return None


def crawl(host):
    s = requests.Session()
    county = host.split('.')[0].replace('assembly', '')
    county = COUNTY.get(county, county)
    seen, pdfs, queue = set(), {}, [(f'https://{host}/', 0)]
    n = 0
    while queue and n < 60:
        u, depth = queue.pop(0)
        if u in seen:
            continue
        seen.add(u)
        r = get(s, u)
        n += 1
        if r is None:
            continue
        if r.status_code in (403, 429):
            log(f'{host} {r.status_code}: stop')
            break
        if r.status_code != 200 or 'html' not in r.headers.get('content-type', ''):
            continue
        for href, t in re.findall(r'<a[^>]+href=["\']([^"\'#]+)["\'][^>]*>(.*?)</a>', r.text, re.S | re.I):
            v = urllib.parse.urljoin(r.url, html.unescape(href.strip()))
            t = html.unescape(re.sub(r'<[^>]+>|\s+', ' ', t)).strip()
            if v.split('/')[2:3] != [r.url.split('/')[2]] and host not in v:
                continue
            if v.lower().endswith('.pdf'):
                fn = urllib.parse.unquote(v.rsplit('/', 1)[-1])
                if POS.search(t + ' ' + fn) and not NEG.search(t + ' ' + fn):
                    pdfs[v] = t or fn
            elif depth < 2 and (NAV.search(t) or NAV.search(v.split(host, 1)[-1])) and v not in seen:
                queue.append((v, depth + 1))
    log(f'{host}: {n} pages, {len(pdfs)} pdfs')
    return [{'county': county, 'host': host, 'title': t, 'url': u, 'wpdate': None} for u, t in pdfs.items()]


out = []
with cf.ThreadPoolExecutor(12) as ex:
    for r in ex.map(crawl, HOSTS):
        out += r
cc = json.loads((W / 'county_cands.json').read_text())
have = {x['url'] for x in cc}
new = [x for x in out if x['url'] not in have]
(W / 'crawl_cands.json').write_text(json.dumps(new, indent=0))
log(f'DONE {len(new)} new')
