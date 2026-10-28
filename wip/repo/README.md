# Kenya: law history in git

The law of Kenya as a git history: one file per provision, one commit per law on the day it took effect, and the law that made each change as the commit's author. `git blame` names the law behind every paragraph; `git log` lists every change to a provision; `tools/on.py` gives the text in force on any day.

It follows the shared design of [lexifina/global-law](https://github.com/lexifina/global-law), which places it at `ke/`. Every version is a dated point-in-time version published by [Kenya Law](https://new.kenyalaw.org) on the Laws.Africa Peachjam platform.

**What is in it now**

| Folder | Act | Versions | History |
| --- | --- | ---: | --- |
| `constitution/` | [CONSTITUTION OF KENYA](https://new.kenyalaw.org/akn/ke/act/2010/constitution) | 1 | 2010-09-03 to 2010-09-03 |
| `companies/` | [COMPANIES ACT](https://new.kenyalaw.org/akn/ke/act/2015/17) | 12 | 2015-09-18 to 2024-12-27 |
| `employment/` | [EMPLOYMENT ACT](https://new.kenyalaw.org/akn/ke/act/2007/11) | 11 | 2008-06-02 to 2024-04-26 |

**CONSTITUTION OF KENYA**

| In force | Author |
| --- | --- |
| 2010-09-03 | Constitution of Kenya, 2010 (as enacted) |

**COMPANIES ACT**

| In force | Author |
| --- | --- |
| 2015-09-18 | Act 17 of 2015 (as enacted) |
| 2017-01-01 | Act No. 38 of 2016; publisher (Kenya Law (National Council for Law Reporting)): 68 provision(s) unexplained |
| 2017-05-04 | Act No. 11 of 2017 |
| 2017-05-16 | Cap. 499A |
| 2017-08-16 | Act No. 28 of 2017 |
| 2019-01-18 | Act No. 18 of 2018 |
| 2019-07-23 | Act No. 12 of 2019 |
| 2020-03-18 | Act No. 1 of 2020 |
| 2021-03-30 | Act No. 1 of 2021 |
| 2022-12-31 | publisher (Kenya Law (National Council for Law Reporting)): 188 provision(s) unexplained |
| 2023-09-15 | Act No. 10 of 2023 |
| 2024-12-27 | Act No. 20 of 2024 |

**EMPLOYMENT ACT**

| In force | Author |
| --- | --- |
| 2008-06-02 | Act 11 of 2007 (as enacted) |
| 2014-12-08 | publisher (Kenya Law (National Council for Law Reporting)): 2 provision(s) unexplained |
| 2018-07-01 | Act No. 10 of 2018, Act No. 19 of 2015; publisher (Kenya Law (National Council for Law Reporting)): 1 provision(s) unexplained |
| 2019-11-07 | Act No. 23 of 2019 |
| 2020-12-11 | Act No. 20 of 2020, Cap. 411C; publisher (Kenya Law (National Council for Law Reporting)): 1 provision(s) unexplained |
| 2021-04-15 | Act No. 2 of 2021 |
| 2022-04-22 | Act No. 15 of 2022 |
| 2022-12-31 | publisher (Kenya Law (National Council for Law Reporting)): 42 provision(s) unexplained |
| 2023-07-01 | Act No. 4 of 2023 |
| 2024-03-22 | Cap. 117A |
| 2024-04-26 | Act No. 3 of 2024 |

Each folder's `README.md` lists every provision, how often it changed and when.

## A lawyer's questions as git commands

| Question | Command |
| --- | --- |
| What did sec-001 say on 2010-09-03? | `python tools/on.py 2010-09-03 constitution sec-001` |
| The same, with raw git (bash) | `git show $(git rev-list -1 --before="2010-09-03T23:59:59Z" main -- constitution/sec-001.md):constitution/sec-001.md` |
| The same, in PowerShell | `$r = git rev-list -1 --before="2010-09-03T23:59:59Z" main -- constitution/sec-001.md; git show "$($r):constitution/sec-001.md"` |
| Which law wrote each line? | `git blame constitution/sec-001.md` |
| Every change, word by word | `git log -p --word-diff constitution/sec-001.md` |
| Every law in the record, in order | `git log --reverse --format="%ad %an" --date=short main` |
| Everything one law changed | `git show law/<key>` (tags `law/<key>` mark each law's commit) |
| The whole act on a date | `python tools/on.py 2010-09-03 constitution` |
| Which law gave a provision its wording on a date | `python tools/on.py --law 2010-09-03 constitution sec-001` |

After a rebuild, refresh tags with `git fetch --force --tags`: a plain fetch keeps stale tags.

## Dates

- Each commit is dated at **noon, Africa/Nairobi, on the day the change took effect**. The day is also in the `In-force:` trailer, which the tools read; enactment (assent) and Gazette publication dates are trailers too, where Kenya Law states them.
- **The day is Kenya Law's.** Each version is a Laws.Africa expression, and its date is the day the amendment it takes in came into force, as the amendment list says ("[Amended by <Act> on <date>]"). For a consolidation (a revised edition) it is the date the edition is as at. An act's original expression is dated by its Gazette publication; where Kenya Law gives a later commencement date ("Commenced on ..."), the first version is dated by that instead (see REPRODUCE.md, decisions).
- `--before="YYYY-MM-DD"` alone uses your clock's time of day, so a law that took effect that day may be missed before noon. Use `T23:59:59Z` as above, or the tool.

## How it is checked

- Every version is read back from git on the day it took effect and on the day before (`tools/check_repo.py`); both must match `corpus.json`. Results are in `REPRODUCE.md`.
- **Against Kenya Law today:** the last version of each act is Kenya Law's current expression, as named by its own legislation listing on the retrieval day, and is the text of that expression page.
- **Every version is its own dated expression**: each was parsed from an archived copy of exactly that expression's page, whose sha256 is recorded with the version.
- The repository is rebuilt from the same data a second time and must give identical hashes.

## What "author" means

The author of a commit is the law that made the change, with an e-mail address that cannot exist, so `git blame` and `git log --author` name laws. The committer is always Lexifina.

- **Credits come only from Kenya Law's own notes.** A version whose History entry names one amending Act is credited to it. Where one version takes in several Acts, or a revised edition, a provision is credited to an Act only if Kenya Law's editorial note in that provision names it ("[section 5 amended by section 2 of Act 3 of 2020]"); the rest are committed by the publisher and labelled "unexplained", and the commit message names the Acts the version takes in.
- **The first commit** is the act as enacted where that is the oldest version; otherwise it is the oldest version available (a consolidation), credited to the publisher.
- Blame credits whole lines (one paragraph per line). Use `git log -p --word-diff` to see exactly which words each change made.

## What it does not show

- **Only the versions Kenya Law publishes.** Changes before its oldest version are not separate commits.
- **Editorial notes.** Kenya Law's bracketed notes ("[Act No. 18 of 1996]", "[section 5 amended by ...]") are left out of the text and used only for credits, except where a provision has no other text (repealed or spent), where the note is what Kenya Law prints and is kept.
- **Headings above the provision** (Part, Chapter, Division) are left out; each file starts with its own number and heading. Footnotes are kept at the end of the file.
- **Amendments not yet applied.** Where the LII lists an amendment as not yet applied to its consolidated text, it is not in this history; REPRODUCE.md lists each one.
- **No OCR.** Acts the LII shows only as scanned PDFs are not included.

## How it is built


## Sources

| Source | What it gives | Used for |
| --- | --- | --- |
| [Kenya Law](https://new.kenyalaw.org) | Dated point-in-time versions (expressions) of each act, its History and amendment list, and per-provision editorial notes; its listing page names the current version | The text and dates of every version |
| [Internet Archive](https://web.archive.org/) | Archived copies of those expression pages | Reading them |

## Licence

See [LICENSE](LICENSE). Source: Kenya Law, the National Council for Law Reporting (https://kenyalaw.org). Raw source documents are made available under the Creative Commons Attribution-NonCommercial 4.0 International licence (CC BY-NC 4.0); NCLR's terms of use require an explicit Licensing Agreement for automated extraction and commercial redistribution.

Kenya Law's terms: Kenya Law terms of use s. 9 (https://kenyalaw.org/terms-of-use/): raw, unannotated source documents CC BY-NC 4.0 crediting NCLR; automated scraping, bulk extraction, commercial redistribution and AI training need an explicit Licensing Agreement from NCLR. Lexifina's arrangement, messages, tables and tools are CC0.

This repository is not legal advice. Kenya's laws are published in English, so there is no separate summary in another language.
