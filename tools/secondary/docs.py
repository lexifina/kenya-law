"""In-place documentation update for the secondary-copy additions: README (what is in it, gaps, sources), REPRODUCE
(a section appended once and refreshed), LICENSE (each new source's terms), tools/secondary/. One commit."""
import json
import re
import shutil
import subprocess
import time
from pathlib import Path

W = Path(r'C:\Users\alany\Documents\kenya-law-work')
R = W / 'repo'
NOWIN = 0x08000000


def git(*a):
    return subprocess.run(['git', '-C', str(R), *a], capture_output=True, text=True, encoding='utf-8',
                          creationflags=NOWIN, check=True).stdout


git('checkout', '-q', '-f', 'main')
base = 'e3456b57dddaf599d269ff866dcfe86c50910ffd'
built = json.loads((W / 'built.json').read_text('utf-8'))
held = json.loads((W / 'held.json').read_text('utf-8'))
new = int(git('rev-list', '--count', f'{base}..main', '--', '.', ':!README.md', ':!REPRODUCE.md', ':!LICENSE', ':!tools'))
total = int(git('rev-list', '--count', 'main')) + 1
vers = built['versions']
la = {k: v for k, v in vers.items() if k.startswith('/akn')}
acts = sorted({v for v in la.values() if '/' not in v})
subs = sum(1 for v in vers.values() if v.startswith('subsidiary/'))
asmade = sum(1 for v in vers.values() if v.startswith('as-made/'))
counties = sum(1 for v in vers.values() if v.startswith('counties/'))
dates = sorted(re.findall(r'^In-force: (\d{4}-\d{2}-\d{2})$', git('log', f'{base}..main', '--format=%B'), re.M))
lo, hi = dates[0], dates[-1]
core = [a for a in ['penal-code', 'criminal-procedure-code', 'evidence', 'civil-procedure', 'land'] if a in acts]

readme = (R / 'README.md').read_text('utf-8')
para = re.search(r'^\*\*What is in it now:\*\*.*$', readme, re.M).group(0)
add = (f' Added on 2026-11-26 from secondary copies (FAOLEX and WIPO Lex; Kenya Law\'s own site was not used): '
       f'{len(set(la.values()))} more consolidated laws as Kenya Law dated them ({len(acts)} Acts, among them the Penal '
       f'Code, the Criminal Procedure Code, the Evidence Act, the Civil Procedure Act and the Land Act 2012), {subs} '
       f'pieces of subsidiary legislation (`subsidiary/<year>/`), {asmade} Acts as made (`as-made/<year>/`)'
       + (f' and {counties} county laws (`counties/`)' if counties else '') +
       f', {new} commits in all, in force from {lo} to {hi}.')
para2 = re.sub(r' Added on 2026-11-26 from secondary copies.*?(?= \[`REPRODUCE|$)', '', para)
para2 = para2.replace(' [`REPRODUCE.md`]', add + ' [`REPRODUCE.md`]', 1)
readme = readme.replace(para, para2)
readme = readme.replace(
    "- **Subsidiary legislation and case law** are not here.",
    "- **Most subsidiary legislation, and case law.** Subsidiary legislation is here only where FAOLEX or WIPO Lex "
    "holds a copy with a text layer and a day it was made; Supreme Court decisions are in a separate private "
    "repository.")
readme = readme.replace(
    "because a version is missing (`REPRODUCE.md` says which and why).",
    "because a version is missing (`REPRODUCE.md` says which and why). The secondary copies added later give one "
    "version of each act, the one FAOLEX or WIPO Lex holds, not its earlier versions; revised editions dated only by "
    "a year, and scans without a text layer, are not here.")
row = ("| [FAOLEX](https://faolex.fao.org) (FAO) and [WIPO Lex](https://www.wipo.int/wipolex) (WIPO) | Copies of Kenya "
       "Law's PDFs (Kenya Law and Laws.Africa, CC BY-NC-SA 4.0) and of Acts and Legal Notices as made | one version "
       "each, as the copy holds it | Secondary copies: every such commit says so in `Source-status:` |")
if 'faolex.fao.org) (FAO)' not in readme:
    readme = re.sub(r'(\| \[Internet Archive\]\(https://web\.archive\.org/\)[^\n]*\n)', lambda m: m.group(1) + row + '\n', readme)
(R / 'README.md').write_text(readme, 'utf-8', newline='\n')

lic = (R / 'LICENSE').read_text('utf-8')
if 'FAOLEX' not in lic:
    lic = lic.replace('Changes made by Lexifina:', (
        'Secondary copies added on 2026-11-26 (each such commit carries a Source-status: secondary copy trailer):\n\n'
        '  FAOLEX, the FAO legislative database, https://faolex.fao.org: copies of national texts, reused under FAO\'s '
        'terms\n  (non-commercial reuse with credit to FAO/FAOLEX): https://www.fao.org/contact-us/terms/en/\n'
        '  WIPO Lex, https://www.wipo.int/wipolex: copies of national texts; WIPO terms of use: '
        'https://www.wipo.int/tools/en/disclaim.html\n'
        '  Many of these copies are Kenya Law PDFs, which state: "There is no copyright on the legislative content of '
        'this\n  document. This PDF copy is licensed under a Creative Commons Attribution NonCommercial ShareAlike 4.0 '
        'License\n  (CC BY-NC-SA 4.0)" (https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode), by Kenya Law and '
        'Laws.Africa.\n  Acts and Legal Notices as made are Kenyan official texts from the Kenya Gazette and its '
        'supplements.\n\n'
        'Changes made by Lexifina:'), 1)
    (R / 'LICENSE').write_text(lic, 'utf-8', newline='\n')

rep = (R / 'REPRODUCE.md').read_text('utf-8')
rep = re.sub(r'\n## Secondary copies \(2026-11-26\)\n.*?(?=\n## What AI did)', '\n', rep, flags=re.S)
why = {}
for v in held.values():
    k = re.sub(r'^[^:]*/eng: ', '', v)[:90]
    why[k] = why.get(k, 0) + 1
sec = [
    '', '## Secondary copies (2026-11-26)', '',
    'Kenya Law (kenyalaw.org, new.kenyalaw.org) now answers automated clients with an AWS WAF challenge, and its terms '
    'of use (s. 9) need a Licensing Agreement for bulk extraction, so it was not used. The commits after '
    f'`{base[:9]}` come from copies published elsewhere, read by `tools/secondary/` (no OCR, no model):', '',
    '- FAOLEX: every Kenyan record in its public sitemaps (1,454), the record\'s data from its page, and its full-text '
    'PDFs (policies, agreements and miscellaneous records left out).',
    '- WIPO Lex: every Kenyan legislation record (88) and its PDFs.',
    "- The Parliament of Kenya's Acts list (34 PDFs): all are Kenya Law revised editions dated only by a year, or "
    'scans, so none is used.', '',
    'Rules:', '',
    '- A Kenya Law / Laws.Africa PDF (cover: "By Kenya Law and Laws.Africa", `FRBR URI: /akn/ke/act/.../eng@DATE`) is '
    'one version, dated by that expression date; its history list gives the change that took effect that day, which '
    'is credited (an Act or Legal Notice), or the publisher for a revision. Provisions are split on the PDF\'s own '
    'section headings; Part and Chapter headings and editorial notes are left out as in the rest of the repository.',
    "- A version of an act already here from Kenya Law's own pages is not added again; a later one is.",
    '- Any other PDF is taken only as the text as made: dated by the "Date of Commencement" printed in it, else by '
    "FAOLEX's day of the text (the day it was made or assented to). A revised edition dated only by a year, a "
    'commencement left to a notice, a record dated only by year, and a scan without a text layer are held.',
    f'- Result: {new} commits; {len(held)} copies held. Reasons held:', '']
for k, n in sorted(why.items(), key=lambda x: -x[1])[:12]:
    sec.append(f'  - {n}: {k}')
sec += ['', 'Not found in any open copy: the Companies Act 2015 and the Employment Act 2007.', '']
rep = rep.replace('\n## What AI did', '\n'.join(sec) + '\n## What AI did', 1)
(R / 'REPRODUCE.md').write_text(rep, 'utf-8', newline='\n')

t = R / 'tools' / 'secondary'
t.mkdir(parents=True, exist_ok=True)
for f in ['build.py', 'lapdf.py', 'pdfread.py', 'fetch_fao.py', 'fetch_wipo.py', 'fetch_parl.py', 'fao_sitemap.py',
          'parl_list.py', 'launch.py', 'docs.py']:
    shutil.copy(W / 'tools' / f, t / f)
git('add', '-A', 'README.md', 'REPRODUCE.md', 'LICENSE', 'tools/secondary')
if git('diff', '--cached', '--name-only').strip():
    env = dict(__import__('os').environ, GIT_AUTHOR_NAME='Lexifina', GIT_AUTHOR_EMAIL='kenya-law@lexifina.com',
               GIT_COMMITTER_NAME='Lexifina', GIT_COMMITTER_EMAIL='kenya-law@lexifina.com')
    subprocess.run(['git', '-C', str(R), 'commit', '-q', '-m',
                    'Documentation: README, REPRODUCE.md and LICENSE for the secondary copies (FAOLEX, WIPO Lex); '
                    'tools/secondary'], env=env, check=True, creationflags=NOWIN)
    print('committed', git('rev-parse', '--short', 'main').strip())

