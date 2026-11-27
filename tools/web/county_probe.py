import json, sys, requests, urllib3, concurrent.futures as cf
urllib3.disable_warnings()
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36'}
C = ('mombasa kwale kilifi tanariver lamu taitataveta garissa wajir mandera marsabit isiolo meru tharakanithi embu kitui '
     'machakos makueni nyandarua nyeri kirinyaga muranga kiambu turkana westpokot samburu transnzoia uasingishu '
     'elgeyomarakwet nandi baringo laikipia nakuru narok kajiado kericho bomet kakamega vihiga bungoma busia siaya '
     'kisumu homabay migori kisii nyamira nairobi').split()


def probe(c):
    out = {}
    for host in (f'{c}assembly.go.ke', f'www.{c}assembly.go.ke', f'{c}.go.ke', f'www.{c}.go.ke'):
        try:
            r = requests.get(f'https://{host}/wp-json/wp/v2/media', params={'mime_type': 'application/pdf', 'per_page': 1},
                             headers=UA, timeout=(10, 25), verify=False)
            out[host] = (r.status_code, r.headers.get('X-WP-Total'))
        except Exception as e:  # noqa: BLE001
            out[host] = (type(e).__name__, None)
    return c, out


res = {}
with cf.ThreadPoolExecutor(8) as ex:
    for c, o in ex.map(probe, C):
        res[c] = o
        print(c, o, flush=True)
json.dump(res, open(r'kenya-law-work\county_probe.json', 'w'), indent=1)
