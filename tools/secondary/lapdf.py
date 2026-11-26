"""Read a Kenya Law / Laws.Africa PDF ("By Kenya Law and Laws.Africa", FRBR URI .../eng@YYYY-MM-DD) from its text layer.

read(bytes) -> dict(ok, frbr, expr_date, as_at, title, cap, assented, commenced, history=[(text, date)], units=[(stem, head, text)])
Rules: running heads, page numbers, Part/Chapter headings and full-line editorial notes ([L.N. ..., Act No. ...]) are left
out; a provision whose only text is a note ([Deleted by ...]) keeps it. The index after the last schedule is left out.
"""
from __future__ import annotations

import datetime as dt
import re

import pymupdf

MON = {m: i for i, m in enumerate(['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
                                    'september', 'october', 'november', 'december'], 1)}
LIG = str.maketrans({'\ufb00': 'ff', '\ufb01': 'fi', '\ufb02': 'fl', '\ufb03': 'ffi', '\ufb04': 'ffl'})
DATE = r'(\d{1,2})\s+([A-Z][a-z]+)\s+((?:1[89]|20)\d\d)'


def day(d, m, y):
    try:
        return dt.date(int(y), MON[m.lower()], int(d)).isoformat()
    except (KeyError, ValueError):
        return None


def is_la(doc) -> bool:
    t = ' '.join(doc[i].get_text() for i in range(min(3, doc.page_count)))
    return 'Laws.Africa' in t and 'FRBR URI' in t


def lines(doc):
    out = []
    for pno, pg in enumerate(doc):
        H = pg.rect.height
        for b in pg.get_text('dict')['blocks']:
            for ln in b.get('lines', []):
                sp = [s for s in ln['spans'] if s['text'].strip()]
                if not sp:
                    continue
                t = re.sub(r'\s+', ' ', ''.join(s['text'] for s in ln['spans'])).strip().translate(LIG)
                x0, y0, x1, y1 = ln['bbox']
                if y0 < 60 or y0 > H - 60:      # running head / page number
                    continue
                out.append(dict(p=pno, x=x0, y=round(y0, 1), y1=y1, t=t, sz=round(max(s['size'] for s in sp), 1),
                                bold=all(s['flags'] & 16 for s in sp)))
    out.sort(key=lambda l: (l['p'], l['y'], l['x']))
    # merge fragments on one baseline
    rows = []
    for l in out:
        if rows and rows[-1][0]['p'] == l['p'] and abs(rows[-1][0]['y'] - l['y']) < 2:
            rows[-1].append(l)
        else:
            rows.append([l])
    return rows


def read(b: bytes) -> dict:
    try:
        doc = pymupdf.open(stream=b, filetype='pdf')
    except Exception as e:  # noqa: BLE001
        return {'ok': False, 'why': f'not a PDF ({type(e).__name__})'}
    if not is_la(doc):
        return {'ok': False, 'why': 'not a Kenya Law / Laws.Africa PDF'}
    head = '\n'.join(doc[i].get_text() for i in range(min(3, doc.page_count)))
    m = re.search(r'FRBR URI:\s*(/akn/\S+?)@(\d{4}-\d{2}-\d{2})', head)
    if not m:
        return {'ok': False, 'why': 'no FRBR expression date'}
    frbr, expr = m.group(1), m.group(2)
    a = re.search(r'(?:Legislation|Gazette|Bill) as at ' + DATE, head)
    as_at = day(*a.groups()) if a else None
    rows = lines(doc)
    # the cover block: title page is page 1 (index 1); the act begins at the first bold title after "Contents"
    first = None
    for i, r in enumerate(rows):
        t = ' '.join(l['t'] for l in r)
        if re.match(r'^(?:Assented to on|Commenced on|Made on|Published in|Not commenced)', t):
            first = i
            break
    if first is None:
        return {'ok': False, 'why': 'no Assented/Commenced line'}
    # title lines just above
    k = first - 1
    title_parts = []
    while k >= 0 and rows[k][0]['bold'] and rows[k][0]['p'] == rows[first][0]['p']:
        title_parts.insert(0, ' '.join(l['t'] for l in rows[k]))
        k -= 1
    meta_txt, hist, i = [], [], first
    while i < len(rows):
        t = ' '.join(l['t'] for l in rows[i])
        if rows[i][0]['bold'] and not re.match(r'^(?:Assented|Commenced|Made|Published|Not commenced)', t):
            break
        meta_txt.append(t)
        i += 1
    mt = ' '.join(meta_txt)
    for h in re.findall(r'\[((?:Amended|Revised|Repealed|Commenced)[^\]]*?)\]', mt):
        d = re.search(r' on ' + DATE + r'\s*$', h)
        hist.append((h, day(*d.groups()) if d else None))
    ass = re.search(r'Assented to on ' + DATE, mt)
    com = re.search(r'Commenced on ' + DATE, mt)
    made = re.search(r'Made on ' + DATE, mt)
    pub = re.search(r'Published in (.*?) on ' + DATE, mt)
    body = rows[i:]
    units, cur = [], None
    pre: list[str] = []
    stop = False

    def flush_line(u, r):
        t = ' '.join(l['t'] for l in sorted(r, key=lambda l: l['x']))
        u['lines'].append((r[0]['p'], r[0]['y'], r[0]['x'], t))

    for r in body:
        t = ' '.join(l['t'] for l in sorted(r, key=lambda l: l['x']))
        l0 = sorted(r, key=lambda l: l['x'])[0]
        bold, sz = l0['bold'], l0['sz']
        if bold and sz >= 11 and re.match(r'^(?:Index|INDEX)\b', t):
            break
        if bold and sz >= 11:
            if re.search(r'\bSchedule\b|\bSCHEDULE\b', t) and re.match(r'^(?:[A-Z][a-z]+\s+)?(?:Schedule|SCHEDULE)|^[A-Z ]*SCHEDULE', t):
                cur = {'kind': 'sch', 'head': t, 'lines': []}
                units.append(cur)
                continue
            if cur and cur['kind'] == 'sch' and not cur['lines']:
                cur['head'] += ' ' + t        # schedule sub-title
                continue
            if cur and cur['kind'] == 'sch':
                flush_line(cur, r)
                continue
            continue                          # Part / Chapter / Division heading
        mm = re.match(r'^(\d+[A-Z]{0,3})\.\s*(.*)$', t)
        if bold and mm and 9.5 <= sz < 11 and (cur is None or cur['kind'] == 'sec'):
            cur = {'kind': 'sec', 'n': mm.group(1), 'head': mm.group(2).strip(), 'lines': []}
            units.append(cur)
            continue
        if cur is None:
            pre.append(t)
            continue
        if cur['kind'] == 'sec' and not cur['lines'] and bold and 9.5 <= sz < 11:
            cur['head'] = (cur['head'] + ' ' + t).strip()   # heading continued on a second line
            continue
        flush_line(cur, r)
    if not units:
        return {'ok': False, 'why': 'no sections read'}

    def text_of(ls):
        out, last = [], None
        for p, y, x, t in ls:
            if re.fullmatch(r'\[[^\[\]]*\]', t) and len(ls) > 1:
                continue
            if last and p == last[0] and 0 < y - last[1] < 14:
                out[-1] += (' ' if not out[-1].endswith('-') else '') + t
            else:
                out.append(t)
            last = (p, y)
        return '\n'.join(out).strip()

    final, seen, nsch = [], set(), 0
    if pre:
        final.append(('preamble', 'Long title and enacting words', '\n'.join(x for x in pre if not re.fullmatch(r'\[[^\[\]]*\]', x))))
    for u in units:
        if u['kind'] == 'sec':
            n = re.match(r'(\d+)([A-Z]*)', u['n'])
            stem = f'sec-{int(n.group(1)):03d}{n.group(2).lower()}'
            head = f"{u['n']}. {u['head']}".strip()
        else:
            nsch += 1
            stem = f'sch-{nsch:02d}'
            head = u['head']
        body_t = text_of(u['lines'])
        if not body_t and u['kind'] == 'sec' and u['head'].startswith('['):
            body_t, head = u['head'], f"{u['n']}."
        s2, k = stem, 2
        while s2 in seen:
            s2, k = f'{stem}-{k}', k + 1
        seen.add(s2)
        final.append((s2, head, body_t))
    nsec = sum(1 for u in units if u['kind'] == 'sec')
    return {'ok': True, 'frbr': frbr, 'expr_date': expr, 'as_at': as_at, 'title': ' '.join(title_parts),
            'assented': day(*ass.groups()) if ass else None, 'commenced': day(*com.groups()) if com else None,
            'made': day(*made.groups()) if made else None,
            'published': (pub.group(1), day(*pub.groups()[1:])) if pub else None,
            'history': hist, 'units': final, 'sections': nsec, 'pages': doc.page_count}
