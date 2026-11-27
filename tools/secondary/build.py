"""Append secondary-copy versions of Kenyan law to kenya-law-work/repo (refs/heads/main), one commit per version,
noon Africa/Nairobi on the day it took effect.

Sources (no request to kenyalaw.org): FAOLEX full-text PDFs, WIPO Lex PDFs, the Parliament of Kenya's Acts list.
 * Kenya Law / Laws.Africa PDFs (cover page "By Kenya Law and Laws.Africa", FRBR URI .../eng@DATE): one version per
   expression, dated by the expression date; provisions split by the PDF's own section headings.
 * Other PDFs: the text as made, dated by the commencement day printed in it, else FAOLEX's day of the text; revised
   editions dated only by a year are held.
State: kenya-law-work/built.json, held.json.     python -X utf8 -I build.py [--dry]
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
import time
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import lapdf  # noqa: E402
import pdfread  # noqa: E402
import pymupdf  # noqa: E402

W = Path(r'kenya-law-work')
REPO = W / 'repo'
NOWIN = 0x08000000
PUB = ('Kenya Law (National Council for Law Reporting)', 'kenyalaw@kenyalaw.invalid')
COUNTIES = {}


def log(m):
    with open(W / 'progress.log', 'a', encoding='utf-8') as f:
        f.write(time.strftime('%H:%M:%S ') + 'build: ' + m + '\n')


def git(*a, check=True):
    r = subprocess.run(['git', '-C', str(REPO), *a], capture_output=True, text=True, encoding='utf-8',
                       creationflags=NOWIN)
    if check and r.returncode:
        raise RuntimeError(f'git {a}: {r.stderr}')
    return r.stdout


def slugify(s, n=60):
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if not unicodedata.combining(c)).lower()
    s = s.replace('&', ' and ').replace("'", '').replace('\u2019', '')
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:n].rstrip('-') or 'law'


def short_slug(title):
    t = re.sub(r'\((?=[^)]*(?:\d|Cap\.|L\.N|No\.))[^)]*\)', '', title)
    t = re.sub(r'[,\s]*(?:No\.?\s*\d+\s+of\s+)?(?:19|20)\d\d\.?\s*$', '', t.strip(), flags=re.I)
    t = re.sub(r'^the\s+', '', t.strip(), flags=re.I)
    s = slugify(t)
    return re.sub(r'-act$', '', s) or s


def noon(d):
    d = dt.date.fromisoformat(d)
    t = dt.datetime(d.year, d.month, d.day, 9, 0, 0, tzinfo=dt.timezone.utc)
    return f'{max(int(t.timestamp()), 32400)} +0300'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def trailers(d):
    return '\n'.join(f'{k}: {v}' for k, v in d.items() if v not in (None, ''))


class FastImport:
    def __init__(self, parent):
        self.p = subprocess.Popen(['git', '-C', str(REPO), 'fast-import', '--quiet', '--done'],
                                  stdin=subprocess.PIPE, creationflags=NOWIN)
        self.parent, self.n = parent, 0

    def _w(self, s):
        self.p.stdin.write(s if isinstance(s, bytes) else s.encode('utf-8'))

    def commit(self, author, date, message, files):
        self.n += 1
        self._w(f'commit refs/heads/main\nmark :{self.n}\n')
        self._w(f'author {author[0]} <{author[1]}> {date}\ncommitter Lexifina <kenya-law@lexifina.com> {date}\n')
        b = message.encode('utf-8')
        self._w(f'data {len(b)}\n')
        self._w(b + b'\n')
        self._w(f'from :{self.n - 1}\n' if self.n > 1 else f'from {self.parent}\n')
        for path, text in files.items():
            if text is None:
                self._w(f'D {path}\n')
            else:
                b = text.encode('utf-8')
                self._w(f'M 100644 inline {path}\ndata {len(b)}\n')
                self._w(b + b'\n')
        self._w(b'\n')

    def close(self):
        self._w(b'done\n')
        self.p.stdin.close()
        if self.p.wait():
            raise RuntimeError('fast-import failed')


def existing():
    """work -> (folder, latest expression date) for the acts already on main (Kenya Law expressions)."""
    out = {}
    for line in git('log', 'main', '--format=%(trailers:key=Consolidated,valueonly,separator=;)').splitlines():
        for m in re.finditer(r'/akn/ke/act/(\d{4}/[\w-]+)/eng@(\d{4}-\d{2}-\d{2})', line):
            w, d = m.group(1), m.group(2)
            if w not in out or d > out[w]:
                out[w] = d
    return out


FOLDERS = {'2010/constitution': 'constitution', '1989/17': 'capital-markets', '2015/29': 'tax-procedures',
           '1995/2': 'kenya-revenue-authority', '2015/23': 'excise-duty', '1963/15': 'estate-duty', '2011/9': 'iebc',
           '1966/15': 'central-bank', '2010/4': 'alcoholic-drinks-control'}


def readme(title, lines, units):
    out = [f'# {title}', '', *lines, '', '| Provision | File |', '| --- | --- |']
    for stem, head, _ in units:
        out.append(f'| {head.replace("|", "/")[:150]} | [{stem}.md]({stem}.md) |')
    return '\n'.join(out) + '\n'


def unit_files(folder, units):
    return {f'{folder}/{s}.md': f'# {h}\n{t.strip()}\n' for s, h, t in units}


def la_title(b):
    doc = pymupdf.open(stream=b, filetype='pdf')
    for i in range(min(3, doc.page_count)):
        ls = [x.strip() for x in doc[i].get_text().split('\n') if x.strip()]
        for j, x in enumerate(ls):
            if re.match(r'^(?:Legislation|Gazette) as at', x) and j >= 2:
                k = j - 1
                parts = []
                while k >= 0 and ls[k] not in ('Kenya',) and not ls[k].startswith('Kenya '):
                    parts.insert(0, ls[k])
                    k -= 1
                if parts:
                    return parts
    return None


def credit(hist, expr, frbr, commenced):
    """Author of an expression: the law its last history entry names, when that entry's day is the expression day."""
    last = [h for h in hist if h[1] == expr]
    if last:
        h = last[-1][0]
        m = re.search(r'\(Act No\. (\d+) of (\d{4})\)', h)
        if m and h.startswith('Amended'):
            return (f'Act No. {m.group(1)} of {m.group(2)}', f'act-{m.group(2)}-{m.group(1)}@kenyalaw.invalid'), 'law', h
        m = re.search(r'\(Legal Notice (\d+) of (\d{4})\)', h)
        if m and h.startswith('Amended'):
            return (f'Legal Notice {m.group(1)} of {m.group(2)}', f'ln-{m.group(2)}-{m.group(1)}@kenyalaw.invalid'), 'law', h
        return PUB, 'publisher', h
    if not hist or all(h[1] is None for h in hist):
        m = re.match(r'/akn/ke(?:-\w+)?/act/(?:(ln|ga)/)?(\d{4})/([\w-]+)', frbr)
        if m and (expr == commenced or not commenced):
            if m.group(1) == 'ln':
                return (f'Legal Notice {m.group(3)} of {m.group(2)}', f'ln-{m.group(2)}-{m.group(3)}@kenyalaw.invalid'), 'law', None
            return (f'Act No. {m.group(3)} of {m.group(2)}', f'act-{m.group(2)}-{m.group(3)}@kenyalaw.invalid'), 'law', None
    return PUB, 'publisher', None


def la_item(b, src, built, have):
    r = lapdf.read(b)
    if not r.get('ok'):
        return None, r.get('why')
    frbr, expr = re.sub(r'/(?:eng|swa)$', '', r['frbr']), r['expr_date']
    m = re.match(r'/akn/(ke(?:-[\w]+)?)/act/(?:(ln|ga)/)?(\d{4})/([\w-]+)$', frbr)
    if not m:
        return None, f'{frbr}: not an act or legal notice'
    place, sub, year, num = m.groups()
    work = f'{year}/{num}' if place == 'ke' and not sub else f'{place}/{sub or "act"}/{year}/{num}'
    key = f'{frbr}@{expr}'
    if key in built['versions']:
        return None, None
    if place == 'ke' and not sub and work in have and expr <= have[work]:
        return None, None          # Kenya Law's own expression already on main
    tparts = la_title(b) or [r['title']]
    capre = r'^(?:Cap\.|Act|No\.|Legal Notice|County|L\.N\.)'
    cap = next((p for p in tparts[1:] if re.match(capre, p)), None)
    if sub and len(tparts) > 1:
        rest = [p for p in tparts[1:] if not re.match(capre, p)]
        title = re.sub(r'\s+', ' ', ' '.join(rest)).strip() or tparts[0]
    else:
        title = tparts[0]
    folder = built['works'].get(work) or FOLDERS.get(work)
    if not folder:
        base = short_slug(title)
        if place != 'ke':
            folder = f'counties/{place[3:]}/{base}'
        elif sub:
            folder = f'subsidiary/{year}/{base}'
        else:
            folder = base
        taken = set(built['works'].values()) | set(FOLDERS.values())
        if folder in taken:
            folder = f'{folder}-{year}-{num}'
        built['works'][work] = folder
    units = r['units']
    files = unit_files(folder, units)
    prev = set(built['files'].get(folder, []))
    for s in prev - {u[0] for u in units}:
        files[f'{folder}/{s}.md'] = None
    author, kind, note = credit(r['history'], expr, frbr, r['commenced'] or r['made'])
    label = f'{title}' + (f' ({cap})' if cap else '')
    basis = ("Kenya Law's expression date (" + frbr + '/eng@' + expr + ')' +
             (f': the day of its last listed change, "{note}"' if note else
              (': the commencement day it states' if expr == (r['commenced'] or r['made']) else '')))
    files[f'{folder}/README.md'] = readme(label, [
        f'Kenya Law\'s version as at {expr} ({frbr}/eng@{expr}), read from the copy published by {src["name"]}: '
        f'<{src["pdf_url"]}>.', '',
        'A secondary copy: Kenya Law\'s own site was not used. Editorial notes in square brackets are left out except '
        'where a provision has no other text. Part and Chapter headings are left out.'], units)
    when = expr
    subj = f'{label}: version of {when}'
    body = (f'{label}, as consolidated by Kenya Law to {when}' +
            (f' ({note})' if note else '') + f'. Text of the copy in {src["name"]} ({src["record"]}).')
    tr = {'Law': author[0] if kind == 'law' else None, 'Kind': kind, 'Enacted': r['assented'],
          'In-force': when, 'In-force-basis': basis,
          'Source': src['pdf_url'], 'Source-sha256': sha(b), 'Source-record': src['record'],
          'Source-status': f'secondary copy ({src["name"]}, {src["pdf_url"]})',
          'Expression': f'{frbr}/eng@{expr}', 'Act': label, 'Provisions': len(units), 'Text-source': 'typeset'}
    msg = f'{subj}\n\n{body}\n\n{trailers(tr)}'
    return dict(key=key, work=work, date=when, author=author, msg=msg, files=files, folder=folder,
                stems=[u[0] for u in units]), None


DOC = r'(\d{1,2})(?:st|nd|rd|th)?\s+([A-Z][a-z]+),?\s+((?:19|20)\d\d)'


def plain_item(b, src, meta, built):
    """A PDF that is not a Kenya Law/Laws.Africa print: the text as made, if dated to a day."""
    if meta.get('date_of_consolidation'):
        return None, 'consolidated text dated by year only (no expression date printed)'
    r = pdfread.read(b)
    if not r.get('ok'):
        return None, r.get('why')
    raw = re.sub(r'\s+', ' ', ' '.join(pg.get_text() for pg in list(pymupdf.open(stream=b, filetype='pdf'))[:4]))
    if re.search(r'Revised Edition \d{4}|\[Rev\.? \d{4}\]|Revised and published by the National Council', raw):
        return None, 'revised edition dated by year only'
    when, basis, enacted = None, None, None
    m = re.search(r'Date of Assent:?\s*' + DOC, raw)
    if m:
        enacted = pdfread.day(*m.groups())
    m = re.search(r'Date of Commencement:?\s*' + DOC, raw)
    if m:
        when, basis = pdfread.day(*m.groups()), 'the date of commencement printed under its title'
    elif enacted and re.search(r'Date of Commencement:?\s*(?:See Section|By Notice|on publication|upon publication)', raw, re.I):
        return None, 'commencement by notice or section: day not printed'
    elif meta.get('date_of_text') and not meta.get('has_partial_date_of_text'):
        when, basis = meta['date_of_text'], "FAOLEX's date of the text (the day it was made or assented to; no " \
                                             'commencement day is printed)'
    if not when:
        return None, 'no day of commencement or making'
    title = re.sub(r'\s+', ' ', meta['title_of_text']).strip().rstrip('.')
    types = {t['name'] for t in meta.get('type_of_text') or []}
    year = when[:4]
    key = f'faolex:{meta["faolex_id"]}' if not meta['faolex_id'].startswith('WIPO') else f'wipo:{meta["faolex_id"][5:]}'
    if key in built['versions']:
        return None, None
    base = short_slug(title)
    if 'Regulation' in types:
        folder = f'subsidiary/{year}/{base}'
    else:
        folder = f'as-made/{year}/{base}'
    taken = set(built['works'].values()) | set(FOLDERS.values())
    if folder in taken:
        folder = f'{folder}-{meta["faolex_id"][-6:].lower().lstrip("-")}'
    built['works'][key] = folder
    units = r['units']
    files = unit_files(folder, units)
    files[f'{folder}/README.md'] = readme(title, [
        f'The text as made, in force from {when} ({basis}). Text of the copy in {src["name"]}: <{src["pdf_url"]}>.', '',
        'Text layer: ' + r['src'] + ('. Sections not split (read as one text).' if r['layout'] == 'whole' else '.')],
        units)
    m = re.search(r'\b(?:Act|Act No\.?)\s*(?:No\.?\s*)?(\d+)\s+of\s+((?:19|20)\d\d)', title)
    ln = re.search(r'L\.\s?N\.\s*(?:No\.\s*)?(\d+)\s+of\s+((?:19|20)\d\d)', title)
    author = (f'Act No. {m.group(1)} of {m.group(2)}', f'act-{m.group(2)}-{m.group(1)}@kenyalaw.invalid') if m else \
        (f'Legal Notice {ln.group(1)} of {ln.group(2)}', f'ln-{ln.group(2)}-{ln.group(1)}@kenyalaw.invalid') if ln else \
        (re.sub(r'\s*\(.*$', '', title)[:80], f'{slugify(title, 40)}@kenyalaw.invalid')
    tr = {'Law': author[0], 'Kind': 'law', 'Enacted': enacted, 'In-force': when, 'In-force-basis': basis,
          'Source': src['pdf_url'], 'Source-sha256': sha(b), 'Source-record': src['record'],
          'Source-status': f'secondary copy ({src["name"]}, {src["pdf_url"]})', 'Act': title,
          'Provisions': len(units), 'Text-source': r['src'],
          'Layout': 'whole text (sections not split)' if r['layout'] == 'whole' else None}
    msg = f'{title}: the text as made, {when}\n\n{title}: the text as made, in force from {when}.\n\n{trailers(tr)}'
    return dict(key=key, work=key, date=when, author=author, msg=msg, files=files, folder=folder,
                stems=[u[0] for u in units]), None


SKIP_TYPES = {'Policy', 'Miscellaneous', 'Agreement'}


def sources():
    """(src, meta, path) for every cached PDF."""
    out = []
    for p in sorted((W / 'cache' / 'faolex' / 'meta').glob('*.json')):
        d = json.loads(p.read_text('utf-8'))
        types = {t['name'] for t in d.get('type_of_text') or []}
        if not types or types & SKIP_TYPES:
            continue
        for n in d.get('links_to_full_text') or []:
            pp = W / 'cache' / 'faolex' / 'pdf' / n
            if pp.exists():
                out.append(({'name': 'FAOLEX (FAO)', 'record': d['_url'], 'pdf_url': 'https://faolex.fao.org/docs/pdf/' + n},
                            d, pp))
    for p in sorted((W / 'cache' / 'wipo').glob('*.json')):
        d = json.loads(p.read_text('utf-8'))
        if re.search(r'Policy|Guideline|Strategy', d.get('title', '') + d.get('Type of Text', '')):
            continue
        for x in d.get('pdfs', []):
            pp = W / 'cache' / 'wipo' / x['name']
            if pp.exists():
                out.append(({'name': 'WIPO Lex (WIPO)', 'record': d['url'], 'pdf_url': x['url']}, {'wipo': d}, pp))
    parl = json.loads((W / 'parl_acts.json').read_text('utf-8')) if (W / 'parl_acts.json').exists() else {}
    import urllib.parse
    for u in parl:
        pp = W / 'cache' / 'parl' / urllib.parse.unquote(u.rsplit('/', 1)[1])
        if pp.exists():
            out.append(({'name': "the Parliament of Kenya's Acts list", 'record':
                         'https://www.parliament.go.ke/the-national-assembly/house-business/acts', 'pdf_url': u},
                        {'parl': True}, pp))
    return out


def main(dry=False):
    bp, hp = W / 'built.json', W / 'held.json'
    built = json.loads(bp.read_text('utf-8')) if bp.exists() else {'versions': {}, 'works': {}, 'files': {}}
    held = {}
    have = existing()
    items, seen_sha = [], set(built.get('shas', []))
    for src, meta, p in sources():
        b = p.read_bytes()
        h = sha(b)
        if h in seen_sha:
            continue
        seen_sha.add(h)
        try:
            doc = pymupdf.open(stream=b, filetype='pdf')
            la = lapdf.is_la(doc)
        except Exception as e:  # noqa: BLE001
            held[src['pdf_url']] = f'unreadable PDF ({type(e).__name__})'
            continue
        try:
            if la:
                it, why = la_item(b, src, built, have)
            elif 'faolex_id' in meta:
                it, why = plain_item(b, src, meta, built)
            elif 'wipo' in meta:
                w = meta['wipo']
                t = re.sub(r',\s*Kenya,\s*WIPO Lex\s*$', '', w.get('title', '')).strip()
                pm = {'faolex_id': 'WIPO-' + w['id'], 'title_of_text': t,
                      'date_of_consolidation': 'y' if re.search(r'as amended|Revised Edition|Amended up', t + ' ' + (w.get('Amended up to') or ''), re.I) else None,
                      'type_of_text': [{'name': 'Regulation'}] if re.search(r'Regulations|Rules|Order', t) else [{'name': 'Legislation'}]}
                it, why = plain_item(b, src, pm, built)
            else:
                it, why = None, 'not a Kenya Law/Laws.Africa print and no record date (revised edition or scan)'
        except Exception as e:  # noqa: BLE001
            it, why = None, f'reader error {type(e).__name__}: {e}'
        if it:
            if any(i['key'] == it['key'] for i in items):
                continue
            it['sha'] = h
            items.append(it)
        elif why:
            held[src['pdf_url']] = why
    hp.write_text(json.dumps(held, ensure_ascii=False, indent=1), 'utf-8')
    if not items:
        log(f'nothing new; held {len(held)}')
        print('nothing new', len(held), 'held')
        return
    items.sort(key=lambda i: (i['date'], i['key']))
    # a later version of the same work removes provisions the earlier one had and this one lacks
    cur = {f: set(s) for f, s in built['files'].items()}
    for it in items:
        prev = cur.get(it['folder'], set())
        for s in prev - set(it['stems']):
            it['files'][f'{it["folder"]}/{s}.md'] = None
        cur[it['folder']] = set(it['stems'])
    if dry:
        for it in items[:40]:
            print(it['date'], it['folder'], it['author'][0], len(it['files']))
        print(len(items), 'items;', len(held), 'held')
        return
    parent = git('rev-parse', 'main').strip()
    fi = FastImport(parent)
    for it in items:
        fi.commit(it['author'], noon(it['date']), it['msg'], it['files'])
    fi.close()
    for it in items:
        built['versions'][it['key']] = it['folder']
        built['files'][it['folder']] = it['stems']
    built['shas'] = sorted(set(built.get('shas', [])) | {it['sha'] for it in items})
    bp.write_text(json.dumps(built, ensure_ascii=False, indent=1), 'utf-8')
    log(f'appended {len(items)} commits; held {len(held)}')
    print(len(items), 'commits;', len(held), 'held')


if __name__ == '__main__':
    main('--dry' in sys.argv)
