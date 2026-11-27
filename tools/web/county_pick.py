"""Pick the legislation PDFs from the county media lists -> county_cands.json."""
import html, json, re, collections, urllib.parse
from pathlib import Path
W = Path(r'kenya-law-work')
COUNTY = {'tanariver': 'tana-river', 'taitataveta': 'taita-taveta', 'tharakanithi': 'tharaka-nithi', 'westpokot': 'west-pokot',
          'transnzoia': 'trans-nzoia', 'uasingishu': 'uasin-gishu', 'elgeyomarakwet': 'elgeyo-marakwet', 'homabay': 'homa-bay',
          'muranga': 'muranga'}
POS = re.compile(r'\bacts?\b|\bregulations?\b|\brules\b|by-?laws?|legal[ _-]notice|gazette[ _-]supplement|\bact[_-]?\d{4}|_act_|-act-|act\.pdf', re.I)
NEG = re.compile(r'\bbill|hansard|order[ _-]paper|votes|report|budget|tender|advert|minutes|statement|circular|policy|'
                 r'strategy|plan\b|programme|notice[ _-]of|invitation|shortlist|vacanc|application|award|memo|speech|'
                 r'proceedings|motion|petition|framework|guidelines?|manual|brochure|newsletter|form\b|template|cidp|'
                 r'estimates|fiscal|audit|quotation|interview|recruit|public[ _-]participation|draft|'
                 r'review|request|evaluation|status|summary|presentation|charter|calendar|schedule[ _-]of', re.I)
out, c = [], collections.Counter()
seen = set()
for p in sorted((W / 'cache' / 'county' / 'list').glob('*.json')):
    host = p.stem
    county = host.split('.')[0].replace('assembly', '')
    county = COUNTY.get(county, county)
    for x in json.loads(p.read_text('utf-8')):
        t = html.unescape(x['title'] or '')
        fn = urllib.parse.unquote(x['url'].rsplit('/', 1)[-1])
        s = t + ' ' + fn
        keep = re.search(r'(?i)\bact\b.{0,6}(19|20)\d\d|regulations.{0,4}(19|20)\d\d', s) and not re.search(r'(?i)\bbill|draft|report|hansard|order paper|budget|tender|statement|summary|impact', s)
        if not POS.search(s) or (NEG.search(s) and not keep):
            continue
        if x['url'] in seen:
            continue
        seen.add(x['url'])
        out.append({'county': county, 'host': host, 'title': t, 'url': x['url'], 'wpdate': x['date']})
        c[county] += 1
json.dump(out, open(W / 'county_cands.json', 'w'), indent=0)
print(len(out), c.most_common())
