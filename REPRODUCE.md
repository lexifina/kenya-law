# How this repository was made (Kenya)

This file is written by the build on 2026-10-28, the day the source data was retrieved. Everything below is enough to rebuild this repository hash for hash.

## Sources

| Source | Address | Retrieved | Requests | Licence |
| --- | --- | --- | ---: | --- |
| Kenya Law (National Council for Law Reporting, on the Laws.Africa Peachjam platform) | <https://kenyalaw.org> | 2026-10-28 | 102 | Kenya Law terms of use s. 9 (https://kenyalaw.org/terms-of-use/): raw, unannotated source documents CC BY-NC 4.0 crediting NCLR; automated scraping, bulk extraction, commercial redistribution and AI training need an explicit Licensing Agreement from NCLR |
| Internet Archive Wayback Machine | <https://web.archive.org> | 2026-10-28 | None | Archived copies of Kenya Law pages; the content's terms are NCLR's |

Every response is cached by the sha256 of its URL, and the table above lists every source with its retrieval date. Lexifina keeps its fetch scripts privately; `tools/parse.py` reads only the cache and writes `corpus.json`, so the same cache always gives the same corpus.

## What is in it

| Act | Title | Versions | Span |
| --- | --- | ---: | --- |
| `constitution` | CONSTITUTION OF KENYA | 1 | 2010-08-27 to 2010-08-27 |
| `capital-markets` | CAPITAL MARKETS ACT | 30 | 1989-12-15 to 2025-12-11 |
| `tax-procedures` | TAX PROCEDURES ACT | 20 | 2016-01-19 to 2025-07-01 |

The build made 47 commits:

| Commits | Kind |
| ---: | --- |
| 3 | first version of an act |
| 42 | one law on its in-force day |
| 2 | changes no amendment note explains, credited to the publisher |

Other counts:
- 0 commits on the branch `future`: laws not yet in force on 2026-10-28.
- 0 commits dated 1 January 1970: in force before 1970, with the real day in their `In-force` trailer.
- 36 laws in the record.
- 85 tags.

## Dates

Each commit is dated at noon (Africa/Nairobi) on the day the change took effect. The other dates, enacted and published, are trailers.

When a law gives no date of its own, the default rule applies: Not applied: every version is dated by Kenya Law's own expression date, the day the amendment it incorporates took effect as Laws.Africa records it. No date is computed from a default rule. https://kenyalaw.org/legislation/

## Commands, in order

```sh
# fill the cache from the sources listed above (network; Lexifina's fetch scripts are kept privately)
python -X utf8 tools/parse.py                  # cache -> corpus.json (no network)
python -X utf8 tools/build.py <folder> --repo <empty folder> --docs-date 2026-10-28
python -X utf8 tools/check_repo.py <repo> --corpus <folder>/corpus.json --write
python -X utf8 tools/build.py <folder> --repo <another empty folder> --docs-date 2026-10-28 --compare <repo>
```

In the main Lexifina repository these files live as follows:
- `fetch.py`, `parse.py` and `repo/`: in `scripts/kenya-law/`.
- `build.py`, `check_repo.py` (`check.py` there) and `on.py`: in `scripts/gitlaw_common/`, with the corpus format in `SCHEMA.md`.

## Exact inputs

- `corpus.json` sha256 `30dd5cddcc6f5b3e6218d18e2fe9c821dede8e7760eec08b130f5adbdbda797b` (2245882 bytes)
- Script blob hashes (`git hash-object`):

| Script | Blob |
| --- | --- |
| build.py | `833a2433a3ea96fd87477ccc7a2ed47dc9e24b48` |
| check.py | `426d4cfb32ce103715be6a00865c0a7bca81a56a` |
| on.py | `644a6c0857fbcc72562032b58d57aa113fee0641` |
| fetch.py | `21195cb4d8e803090a7cc303f3ffc83d1623e398` |
| parse.py | `7222235e308f408b3d33658a169852cbe7816ce1` |

- Tools:
  - Python 3.14.0
  - git version 2.52.0.windows.1
  - curl 8.21.0 (Windows) libcurl/8.21.0 Schannel zlib/1.3.2 WinIDN WinLDAP

## Checks

Not yet run for this build.

Not yet run for this build.

These results are from the check run on the build before this one, from the same corpus.

## Decisions made by hand

- Acts were chosen by what the archives hold: the Constitution of Kenya 2010 (1 expression), the Capital Markets Act (all 30 expressions) and the Tax Procedures Act 2015 (all 20). The Penal Code (Cap. 63) has only 3 archived expressions and the Data Protection Act 2019 2, so they were not taken.
- The Companies Act 2015 was tried and dropped: Kenya Law gives no single commencement date ("Commenced"; "Note: 6th November 2015— Parts 1 to 14, 23, 31, 32, 38, 40, 42, 1st Schedule and 6th Schedule; 15th June 2016—All other parts"), and lists the two commencement notices as amendments without versions of their own, so its first version could not be dated by when each Part took effect.
- The Employment Act 2007 was tried and dropped: 2 of its 11 expressions (2017-07-03, 2019-11-25) have no archived copy, so the changes of Act No. 19 of 2015 (in force 2017-07-03, as Kenya Law dates it) could only be dated a year late.
- Licence and terms: Kenya Law's terms of use (s. 9) make only raw, unannotated source documents CC BY-NC 4.0, and prohibit automated data scraping, bulk extraction, commercial redistribution and AI training without an explicit Licensing Agreement from NCLR; its robots.txt sends Content-Signal ai-train=no, ai-input=no and Crawl-delay 5, and its pages answer automated clients with an AWS WAF challenge. No Kenya Law page was fetched for law text: every version is read from the Internet Archive's copy, at most one archive.org request per 3 seconds, for the configured acts only. The user decided on 2026-10-28 that reading these archived copies is acceptable (relayed by the coordinator: "scraping wayback is fair game, dont overdo it, we need this data and it is legal"). The repository stays private. No legal text was given to a model.
- Version dates are Kenya Law's expression dates. Laws.Africa's terminology guide (https://docs.laws.africa/getting-started/terminology-guide) says "Amendments to Principal works come into force on the Commencement date of the Amending work" and that the first point in time is "the work as originally published"; so an amendment's expression is dated by its commencement (in force), and an act's original expression by its publication, which is replaced by the commencement date the page states.
- Credits: a version whose History names exactly one amending law (and no consolidation) between it and the previous version is credited to that law for every provision that changed. Otherwise a provision is credited only to laws that Kenya Law's editorial note inside that provision links to; the rest are unexplained (publisher).
- Editorial notes (akn-remark) are left out of the text and used only as credit evidence, except where a provision has no other text (repealed or spent), where the note is the provision's whole printed content.
- Part, Chapter and Division headings are left out; each provision file starts with its own number and heading. Every other text of each version is in a provision file: parse.py checks this per version (verification.json, fidelity).
- Constitution: the first version is dated 2010-08-27, the commencement date Kenya Law states ("Commenced on 27 August 2010 by Promulgation"), not 2010-09-03, the date of its expression (Gazette publication).
- Tax Procedures Act: the first version is dated 2016-01-19, the commencement date Kenya Law states ("Commenced on 19 January 2016 by Tax Procedures Act Commencement"), not 2015-12-24, the date of its expression (Gazette publication).

## What AI did and did not do

The fetch, parse and check scripts were written by Claude Code running Claude Opus 5.5 (`claude-opus-5-5`) under Lexifina's direction.

No model wrote, translated or corrected legal text. No model runs at build time. Every word of law in this repository comes from the official sources above, through code that anyone can rerun.

The commit messages are written by `build.py` from the source data.

Model use at data-build time:
- Claude Code (Claude Opus 5.5, claude-opus-5-5) wrote the adapter and configuration and chose the acts. No model wrote, summarised or transformed legal text: parse.py is deterministic code.
