"""Append Kenyan legislation read from official government websites (county assemblies / county governments,
ministries and regulators) to kenya-law-work/repo main: one commit per text, noon Nairobi on the day it took effect.

Dating (from the PDF's own text only):
 * Acts: the "Date of Commencement" printed under the title; "on publication" -> the date of the Gazette Supplement
   that carries it. Commencement by notice / not printed -> held.
 * Legal notices / regulations / by-laws: the day they say they come into operation; otherwise the date of the
   Gazette Supplement that published them (subsidiary legislation comes into operation on publication unless it
   says otherwise). No day -> held.
 * Revised editions / consolidations dated by year only -> held.
State: built.json (shared with build.py: versions/works/files/shas), web_held.json.   python -X utf8 -I web_build.py [--dry]
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build as B  # noqa: E402
import pdfread  # noqa: E402
import pymupdf  # noqa: E402

W = B.W
DATE = r'(\d{1,2})\s*(?:st|nd|rd|th|ST|ND|RD|TH)?\s*(?:day of\s+)?([A-Za-z]{3,10})\s*,?\s*((?:19|20)\d\d)'
COUNTY_NAME = {'tana-river': 'Tana River', 'taita-taveta': 'Taita Taveta', 'tharaka-nithi': 'Tharaka Nithi',
               'west-pokot': 'West Pokot', 'trans-nzoia': 'Trans Nzoia', 'uasin-gishu': 'Uasin Gishu',
               'elgeyo-marakwet': 'Elgeyo Marakwet', 'homa-bay': 'Homa Bay', 'muranga': "Murang'a"}
ALLC = ['Mombasa', 'Kwale', 'Kilifi', 'Tana River', 'Lamu', 'Taita[ -]Taveta', 'Garissa', 'Wajir', 'Mandera', 'Marsabit',
        'Isiolo', 'Meru', 'Tharaka[ -]Nithi', 'Embu', 'Kitui', 'Machakos', 'Makueni', 'Nyandarua', 'Nyeri', 'Kirinyaga',
        "Murang'?a", 'Kiambu', 'Turkana', 'West Pokot', 'Samburu', 'Trans[ -]Nzoia', 'Uasin Gishu', 'Elgeyo[ /-]?Marakwet',
        'Nandi', 'Baringo', 'Laikipia', 'Nakuru', 'Narok', 'Kajiado', 'Kericho', 'Bomet', 'Kakamega', 'Vihiga', 'Bungoma',
        'Busia', 'Siaya', 'Kisumu', 'Homa Bay', 'Migori', 'Kisii', 'Nyamira', 'Nairobi']
NAT = set()
if (W / 'nat_probe.json').exists():
    NAT = set(json.loads((W / 'nat_probe.json').read_text()))


def d(m):
    return pdfread.day(*m.groups()) if m else None


def pub_date(raw):
    for m in re.finditer(r'Gazette\s+Supplement', raw, re.I):
        mm = re.search(DATE + r'\s*$', raw[max(0, m.start() - 40):m.start()]) or re.search(DATE, raw[m.end():m.end() + 260])
        if mm:
            x = d(mm)
            if x:
                return x
    return None


def title_of(raw, wp):
    m = re.search(r"(?:may|shall) be cited as\s+(?:the\s+)?([A-Z][^.;:]{3,160}?),?\s*((?:19|20)\d\d)\b", raw)
    if m:
        t = 'The ' + re.sub(r'^[Tt]he\s+', '', m.group(1).strip()) + ', ' + m.group(2)
        return re.sub(r'\s+', ' ', t)
    m = re.search(r"\bTHE\s+((?:(?!THE\s|PRINTER|NAIROBI)[A-Z0-9 ,()'’&\-]){3,140}?\b(?:ACT|REGULATIONS|RULES|BY-LAWS|BYLAWS|ORDER))\s*,?\s*((?:19|20)\d\d)", raw)
    if m:
        t = 'The ' + m.group(1).title().replace("'S ", "'s ").replace('’S ', '’s ') + ', ' + m.group(2)
        return re.sub(r'\s+', ' ', t)
    t = html.unescape(wp)
    t = re.sub(r'[_]+', ' ', t)
    t = re.sub(r'\s*[-–]\s*(?:copy|\d)\s*$|\(\d\)\s*$', '', t, flags=re.I)
    return re.sub(r'\s+', ' ', t).strip()


def parsed(b):
    import pickle
    p = W / 'cache' / 'webparse' / (B.sha(b) + '.pkl')
    if not p.exists():
        return None, None             # not parsed yet (prewarm.py)
    return pickle.loads(p.read_bytes())


def item(b, c, built, taken):
    r, raw = parsed(b)
    if r is None:
        return None, 'pending'
    if not r.get('ok'):
        return None, r.get('why')
    if re.search(r'Revised Edition \d{4}|\[Rev\.? \d{4}\]|Revised and published by the National Council|'
                 r'Laws of Kenya\b.{0,40}\bRevised|^\s*LAWS OF KENYA\b|consolidated (?:version|text)', raw, re.I):
        return None, 'revised edition dated by year only'
    if re.search(r'(?i)with[-_ ]\d{4}[-_ ]amendments|as[-_ ]amended|amended[-_ ]\d{4}|consolidat|revised', c['url'] + ' ' + c['title']):
        return None, 'consolidated/amended copy (no version date)'
    if re.search(r'\bA Bill for\b|\bBILL,? (?:19|20)\d\d\b', raw[:3000]) and not re.search(r'Date of Assent', raw):
        return None, 'a bill'
    is_act = bool(re.search(r'Date of Assent|\bENACTED by\b|AN ACT of the County Assembly|AN ACT of Parliament', raw, re.I))
    when = basis = enacted = None
    m = re.search(r'Date of Assent\s*:?\s*' + DATE, raw, re.I)
    enacted = d(m)
    pub = pub_date(raw)
    m = re.search(r'Date of Commencement\s*:?\s*' + DATE, raw, re.I)
    if m and d(m):
        when, basis = d(m), 'the date of commencement printed under its title'
    elif re.search(r'Date of Commencement\s*:?\s*(?:on|upon|the date of)\s*(?:its\s*)?(?:publication|gazettement)', raw, re.I) and pub:
        when, basis = pub, ('commencement "on publication", printed under its title; published in the Gazette '
                            f'Supplement dated {pub}')
    elif is_act:
        m = re.search(r'(?:come|came|comes)\s+into\s+(?:operation|force|effect)\s*(?:as [^.]{0,80}?)?\s*(?:on|upon|with effect from)\s+(?:the\s+)?'
                      r'(?:(date\s+of\s+(?:its\s+)?publication|publication|gazettement|assent)|' + DATE + r')', raw, re.I)
        if not m or re.search(r'by notice', raw[m.start():m.start() + 200], re.I):
            return None, 'commencement by notice or not printed'
        if m.group(1):
            if re.search(r'assent', m.group(1), re.I):
                if not enacted:
                    return None, 'commences on assent: date of assent not printed'
                when, basis = enacted, 'section 1: comes into operation on assent; the date of assent printed under its title'
            else:
                if not pub:
                    return None, 'commences on publication: Gazette Supplement date not printed'
                when, basis = pub, f'section 1: comes into operation on publication in the Gazette; published in the Gazette Supplement dated {pub}'
        else:
            when = pdfread.day(m.group(2), m.group(3), m.group(4))
            basis = 'the day of coming into operation stated in its commencement section'
            if not when:
                return None, 'commencement day unreadable'
    else:
        m = re.search(r'(?:shall|will)\s+(?:come|be)\s+into\s+(?:operation|force|effect)\s+on\s+(?:the\s+)?' + DATE, raw, re.I)
        m2 = re.search(r'(?:shall|will)\s+(?:come|be)\s+into\s+(?:operation|force|effect)\s+on\s+(?:the\s+)?([A-Z][a-z]{2,8})\.?\s+(\d{1,2}),?\s+((?:19|20)\d\d)', raw)
        if m and d(m):
            when, basis = d(m), 'the day of coming into operation the instrument states'
        elif m2 and pdfread.day(m2.group(2), m2.group(1), m2.group(3)):
            when, basis = pdfread.day(m2.group(2), m2.group(1), m2.group(3)), 'the day of coming into operation the instrument states'
        elif re.search(r'(?:shall|will)\s+(?:come|be)\s+into\s+(?:operation|force|effect)\s+(?:on\s+(?:such|a)\s+date|by notice)', raw, re.I):
            return None, 'commencement by notice: day not printed'
        elif pub and re.search(r'LEGAL NOTICE|Legal Notice No|Legislative Supplement', raw):
            when, basis = pub, ('the date of the Gazette Supplement that published it (subsidiary legislation comes '
                                'into operation on publication unless it says otherwise)')
    if not when:
        return None, 'no day of commencement or publication printed'
    if enacted and when < enacted and when < '1963':
        return None, 'date earlier than assent'
    title = title_of(raw, c['title'])
    if re.search(r'LEGAL NOTICE|Legislative Supplement', raw[:3000], re.I) and re.search(r'\bAct,? (?:19|20)\d\d$', title):
        t2 = re.search(r"THE\s+((?:(?!THE\s)[A-Z0-9 ,()'’&\-]){3,160}?\b(?:REGULATIONS|RULES|ORDER|BY-LAWS))\s*,?\s*((?:19|20)\d\d)", raw)
        title = ('The ' + t2.group(1).title() + ', ' + t2.group(2)) if t2 else re.sub(r'[-_]+', ' ', c['title']).strip()
    host = c['host']
    county = None if host in NAT else c['county']
    if county and (re.search(r'AN ACT of Parliament|ENACTED by the Parliament of Kenya', raw, re.I) or not re.search(r'County Assembly|County Gazette|County Government|County Executive|' + re.escape(COUNTY_NAME.get(county, county).split()[0]) + r'\W+County', raw, re.I)):
        county = None
    if not county and not c.get('region'):
        mm = re.search(r'\b(' + '|'.join(ALLC) + r')(?: City)? County\b', title, re.I)
        if mm and not re.search(r'AN ACT of Parliament', raw, re.I):
            county = B.slugify(mm.group(1).replace("'", ''))
    year = when[:4]
    slug = B.short_slug(title)
    if county:
        slug = re.sub(r'^(?:the-)?' + re.escape(county) + r'(?:-city)?-county-', '', slug) or slug
    sub = bool(re.search(r'LEGAL NOTICE\s+No', raw[:4000], re.I)) or (bool(re.search(r'Regulations|Rules|By-?laws|Order\b', title, re.I)) and not re.search(r'\bAct,', title))
    if c.get('region') == 'eac':
        folder = f'eac/acts/{year}/{slug}'
    elif county:
        folder = f'counties/{county}/{"subsidiary" if sub else "acts"}/{year}/{slug}'
    else:
        folder = f'{"subsidiary" if sub else "as-made"}/{year}/{slug}'
    dupkey = (folder, when)
    if folder in taken:
        return None, None                  # same instrument already built (another copy)
        folder = f'{folder}-{when}'
        if folder in taken:
            return None, None
    taken[folder] = when
    key = 'web:' + c['url']
    built['works'][key] = folder
    units = r['units']
    files = B.unit_files(folder, units)
    who = (f'the County Assembly of {COUNTY_NAME.get(county, county.title())} / County Government website ({host})'
           if county else f'{c["secondary"]} (a secondary copy)' if c.get('secondary') else 'the East African Legislative Assembly website (an Act of the East African Community, which applies in Kenya)' if c.get('region') == 'eac' else f'the website of {host}')
    files[f'{folder}/README.md'] = B.readme(title, [
        f'The text as made, in force from {when} ({basis}). Text of the copy on {who}: <{c["url"]}>.', '',
        'Text layer: ' + r['src'] + ('. Sections not split (read as one text).' if r['layout'] == 'whole' else '.')],
        units)
    m = re.search(r'\b(?:Act\s+)?No\.?\s*(\d+)\s+of\s+((?:19|20)\d\d)', raw[:4000])
    ln = re.search(r'LEGAL NOTICE\s+No\.?\s*(\d+)', raw[:4000], re.I)
    if ln:
        author = (f'Legal Notice No. {ln.group(1)} of {year}', f'ln-{year}-{ln.group(1)}@kenyalaw.invalid')
    elif m and is_act:
        who_a = f'{COUNTY_NAME.get(county, county.title())} County ' if county else 'East African Community ' if c.get('region') == 'eac' else ''
        author = (f'{who_a}Act No. {m.group(1)} of {m.group(2)}',
                  f'{(county + "-") if county else ("eac-" if c.get("region") == "eac" else "")}act-{m.group(2)}-{m.group(1)}@kenyalaw.invalid')
    else:
        author = (title[:80], f'{B.slugify(title, 40)}@kenyalaw.invalid')
    tr = {'Law': author[0], 'Kind': 'law', 'Enacted': enacted, 'In-force': when, 'In-force-basis': basis,
          'Source': c['url'], 'Source-sha256': B.sha(b), 'Source-record': c.get('record') or f'https://{host}/',
          'Source-status': f'secondary copy ({c["secondary"]}, {c["url"]})' if c.get('secondary') else f'official website copy ({host})', 'Act': title,
          'County': COUNTY_NAME.get(county, county.title()) if county else None,
          'Provisions': len(units), 'Text-source': r['src'],
          'Layout': 'whole text (sections not split)' if r['layout'] == 'whole' else None}
    msg = f'{title}: the text as made, {when}\n\n{title}: the text as made, in force from {when}.\n\n{B.trailers(tr)}'
    return dict(key=key, work=key, date=when, author=author, msg=msg, files=files, folder=folder,
                stems=[u[0] for u in units]), None


def main(dry=False):
    bp, hp = W / 'built.json', W / 'web_held.json'
    built = json.loads(bp.read_text('utf-8'))
    held = {}
    taken = {}
    for k, f in built['works'].items():
        taken.setdefault(f, '?')
    seen_sha = set(built.get('shas', []))
    cands = []
    for f in ('county_cands.json', 'nat_cands.json', 'crawl_cands.json'):
        if (W / f).exists():
            cands += json.loads((W / f).read_text('utf-8'))
    items = []
    have = None
    for c in cands:
        key = 'web:' + c['url']
        if key in built['versions']:
            continue
        p = W / 'cache' / 'web' / (hashlib.sha1(c['url'].encode()).hexdigest() + '.pdf')
        if not p.exists():
            continue
        b = p.read_bytes()
        h = B.sha(b)
        if h in seen_sha:
            continue
        seen_sha.add(h)
        try:
            la = False
            if not c.get('secondary'):
                try:
                    la = B.lapdf.is_la(pymupdf.open(stream=b, filetype='pdf'))
                except Exception:  # noqa: BLE001
                    la = False
            if la:
                if have is None:
                    have = B.existing()
                src = {'name': f'the website of {c["host"]}', 'record': f'https://{c["host"]}/', 'pdf_url': c['url']}
                it, why = B.la_item(b, src, built, have)
                if it:
                    it['folder_taken'] = True
            else:
                it, why = item(b, c, built, taken)
        except Exception as e:  # noqa: BLE001
            it, why = None, f'reader error {type(e).__name__}: {e}'
        if it:
            it['sha'] = h
            items.append(it)
        elif why == 'pending':
            seen_sha.discard(h)
        elif why:
            held[c['url']] = why
    hp.write_text(json.dumps(held, ensure_ascii=False, indent=1), 'utf-8')
    if not items:
        B.log(f'web: nothing new; held {len(held)}')
        print('nothing new', len(held), 'held')
        return
    items.sort(key=lambda i: (i['date'], i['key']))
    cur = {f: set(s) for f, s in built['files'].items()}
    for it in items:
        prev = cur.get(it['folder'], set())
        for s in prev - set(it['stems']):
            it['files'][f'{it["folder"]}/{s}.md'] = None
        cur[it['folder']] = set(it['stems'])
    if dry:
        for it in items:
            print(it['date'], it['folder'], '|', it['msg'].split(chr(10))[0][:90], len(it['files']))
        print(len(items), 'items;', len(held), 'held')
        return
    parent = B.git('rev-parse', 'main').strip()
    fi = B.FastImport(parent)
    for it in items:
        fi.commit(it['author'], B.noon(it['date']), it['msg'], it['files'])
    fi.close()
    for it in items:
        built['versions'][it['key']] = it['folder']
        built['files'][it['folder']] = it['stems']
    built['shas'] = sorted(set(built.get('shas', [])) | {it['sha'] for it in items})
    bp.write_text(json.dumps(built, ensure_ascii=False, indent=1), 'utf-8')
    B.log(f'web: appended {len(items)} commits; held {len(held)}')
    print(len(items), 'commits;', len(held), 'held')


if __name__ == '__main__':
    main('--dry' in sys.argv)
