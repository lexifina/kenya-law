"""Update README / LICENSE / REPRODUCE in place for the 2026-11-27 official-website lane and copy its tools into
tools/web/. Prints the numbers; the caller commits."""
import collections, re, shutil, subprocess
from pathlib import Path
W = Path(r'kenya-law-work')
R = W / 'repo'


def git(*a):
    return subprocess.run(['git', '-C', str(R), *a], capture_output=True, text=True, encoding='utf-8').stdout


log = git('log', 'main', '--format=%x1e%(trailers:key=Source-status,valueonly)%x1f%(trailers:key=County,valueonly)%x1f%(trailers:key=Source,valueonly)%x1f%(trailers:key=In-force,valueonly)%x1f%s')
n = collections.Counter()
counties = set()
days = []
for rec in log.split('\x1e')[1:]:
    st, county, src, inf, subj = (x.strip() for x in rec.split('\x1f'))
    web = st.startswith('official website copy')
    sec2 = 'Text of the copy' in subj or False
    if web and county:
        n['county'] += 1
        counties.add(county)
    elif web and 'eala.org' in src:
        n['eac'] += 1
    elif web:
        n['national'] += 1
    else:
        continue
    days.append(inf)
# secondary copies re-read by the commencement reader (web: keys from FAOLEX/WIPO)
import json
built = json.loads((W / 'built.json').read_text('utf-8'))
n['secondary'] = sum(1 for k in built['versions'] if k.startswith('web:https://faolex') or k.startswith('web:https://wipolex'))
total = int(git('rev-list', '--count', 'main').strip())
print(dict(n), len(counties), min(days) if days else None, max(days) if days else None, total)

add = (f' Added on 2026-11-27 from official government websites: {n["county"]} county Acts and regulations of '
       f'{len(counties)} counties (`counties/<county>/acts/<year>/`, `counties/<county>/subsidiary/<year>/`), read from '
       f'county assembly and county government sites; {n["national"]} national Acts, regulations and legal notices as '
       f'made, from the Parliament of Kenya and ministry and regulator sites (`as-made/<year>/`, `subsidiary/<year>/`); '
       f'and {n["eac"]} Acts of the East African Community (`eac/acts/<year>/`), from the East African Legislative '
       f'Assembly. {n["secondary"]} more FAOLEX and WIPO Lex copies were dated by their own commencement sections or '
       f'Gazette Supplement dates.')
p = R / 'README.md'
t = p.read_text('utf-8')
t = re.sub(r' Added on 2026-11-27 from official government websites:.*?Gazette Supplement dates\.', '', t, flags=re.S)
t = t.replace(' [`REPRODUCE.md`](REPRODUCE.md) lists every act', add + ' [`REPRODUCE.md`](REPRODUCE.md) lists every act', 1)
p.write_text(t, 'utf-8')

p = R / 'LICENSE'
t = p.read_text('utf-8')
blk = """
Official website copies added on 2026-11-27 (each such commit carries a Source-status: official website copy trailer
naming the host):

  County Acts and regulations as published in the county gazette supplements, from the websites of Kenya's county
  assemblies and county governments (<county>assembly.go.ke, <county>.go.ke); national Acts, regulations and legal
  notices as published in the Kenya Gazette and its supplements, from the Parliament of Kenya (www.parliament.go.ke)
  and ministry and regulator websites (for example kilimo.go.ke, nema.go.ke, cma.or.ke, centralbank.go.ke,
  treasury.go.ke, epra.go.ke); Acts of the East African Community from the East African Legislative Assembly
  (https://www.eala.org). These are official legislative texts; the sites state no reuse terms of their own for them.
"""
if 'Official website copies added on 2026-11-27' not in t:
    t = t.replace('\nChanges made by Lexifina:', blk + '\nChanges made by Lexifina:', 1)
p.write_text(t, 'utf-8')

p = R / 'REPRODUCE.md'
t = p.read_text('utf-8')
sec = """
## Official website copies (2026-11-27)

`tools/web/` rebuilds these commits. `county_probe.py` and `nat_probe.py` find the county and national sites that
publish a WordPress media list; `county_list.py` / `nat_list.py` list their PDFs; `crawl_list.py` walks the
legislation pages of county sites without one; `page_list.py` reads the Treasury and EPRA legislation pages;
`eac_list.py` the EALA Acts page; `county_pick.py` keeps the titles that read as Acts, regulations, rules, by-laws or
legal notices (not bills, reports, budgets, tenders, drafts or guidelines). `web_fetch.py` downloads them (one request
a second per host; a 403 or 429 stops that host). `prewarm.py` reads each PDF's text layer in its own process
(`parse_one.py`, the same `pdfread.py` as the secondary copies; scans without a text layer are held, no OCR).
`web_build.py` dates each text from its own words only: the Date of Commencement printed under an Act's title; for
"See section 1", the day section 1 gives, or the date of the Gazette Supplement for "on publication", or the Date of
Assent for "on assent"; for regulations and legal notices, the day they say they come into operation, else the date of
the Gazette Supplement that published them. Commencement by notice, undated copies, drafts, bills, revised editions
and consolidations are held (`web_held.json`). A county site's copy of a national Act is filed as national.
`held_to_cands.py` passes the FAOLEX and WIPO Lex copies held for want of a day through the same reader.
"""
if '## Official website copies (2026-11-27)' not in t:
    t = t.rstrip('\n') + '\n' + sec
p.write_text(t, 'utf-8')

d = R / 'tools' / 'web'
d.mkdir(parents=True, exist_ok=True)
for f in ('county_probe.py', 'nat_probe.py', 'nat_probe2.py', 'county_list.py', 'nat_list.py', 'crawl_list.py',
          'page_list.py', 'eac_list.py', 'county_pick.py', 'web_fetch.py', 'prewarm.py', 'parse_one.py', 'web_build.py',
          'held_to_cands.py', 'loop.py', 'docs_web.py'):
    if (W / 'tools' / f).exists():
        (d / f).write_text((W / 'tools' / f).read_text('utf-8-sig').replace(str(W), 'kenya-law-work'), 'utf-8')
for q in list(d.glob('*.py')) + list((R / 'tools' / 'secondary').glob('*.py')):
    x = q.read_text('utf-8')
    y = re.sub(r'C:[\\\\/]+Users[\\\\/]+[^\\\\/]+[\\\\/]+Documents[\\\\/]+', '', x)
    if y != x:
        q.write_text(y, 'utf-8')
