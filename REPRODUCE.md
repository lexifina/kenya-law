# How this repository was made (Kenya)

This file is written by the build on 2026-10-29, the day the source data was retrieved.

## Sources

| Source | Address | Retrieved | Licence |
| --- | --- | --- | --- |
| Kenya Law (National Council for Law Reporting, on the Laws.Africa Peachjam platform) | <https://kenyalaw.org> | 2026-10-28 | Kenya Law terms of use s. 9 (https://kenyalaw.org/terms-of-use/): raw, unannotated source documents CC BY-NC 4.0 crediting NCLR; commercial redistribution and AI training need an explicit Licensing Agreement from NCLR |
| Internet Archive Wayback Machine | <https://web.archive.org> | 2026-10-28 | Archived copies of Kenya Law pages; the content's terms are NCLR's |
| Kenya Law (National Council for Law Reporting, on the Laws.Africa Peachjam platform) | <https://kenyalaw.org> | 2026-10-29 | Kenya Law terms of use s. 9 (https://kenyalaw.org/terms-of-use/): raw, unannotated source documents CC BY-NC 4.0 crediting NCLR; commercial redistribution and AI training need an explicit Licensing Agreement from NCLR |

Every word of law in this repository comes from these sources. Lexifina reads them and records each act's dated versions, and the laws that made each change, in one corpus file. This repository is built from that file.

## What is in it

| Act | Title | Versions | Span |
| --- | --- | ---: | --- |
| `constitution` | CONSTITUTION OF KENYA | 1 | 2010-08-27 to 2010-08-27 |
| `capital-markets` | CAPITAL MARKETS ACT | 30 | 1989-12-15 to 2025-12-11 |
| `tax-procedures` | TAX PROCEDURES ACT | 20 | 2016-01-19 to 2025-07-01 |
| `kenya-revenue-authority` | KENYA REVENUE AUTHORITY ACT | 38 | 1995-07-01 to 2025-08-26 |
| `excise-duty` | EXCISE DUTY ACT | 19 | 2015-12-01 to 2025-07-01 |
| `estate-duty` | ESTATE DUTY ACT | 12 | 1963-06-12 to 1991-12-27 |
| `iebc` | INDEPENDENT ELECTORAL AND BOUNDARIES COMMISSION ACT | 11 | 2011-07-05 to 2024-07-19 |
| `central-bank` | CENTRAL BANK OF KENYA ACT | 10 | 1969-06-03 to 2025-11-04 |
| `alcoholic-drinks-control` | ALCOHOLIC DRINKS CONTROL ACT | 10 | 2010-11-22 to 2023-07-01 |

The build made 128 commits:

| Commits | Kind |
| ---: | --- |
| 9 | first version of an act |
| 110 | one law on its in-force day |
| 9 | changes no amendment note explains, credited to the publisher |

Other counts:
- 0 commits on the branch `future`: laws not yet in force on 2026-10-29.
- 4 commits dated 1 January 1970: in force before 1970, with the real day in their `In-force` trailer.
- 99 laws in the record.
- 232 tags.

## Dates

Each commit is dated at noon (Africa/Nairobi) on the day the change took effect. The other dates, enacted and published, are trailers.

When a law gives no date of its own, the default rule applies: Not applied: every version is dated by Kenya Law's own expression date, the day the amendment it incorporates took effect as Laws.Africa records it. No date is computed from a default rule. https://kenyalaw.org/legislation/

## How the history is built

`tools/build.py` turns the corpus into this history in one pass: one commit per law, on the day it took effect. The same corpus always gives the same commit hashes. `tools/check_repo.py` reads every version back from git and compares it with the corpus. `tools/on.py` shows the law as it stood on any date. The corpus format is described in `tools/SCHEMA.md`.

- Corpus: sha256 `4a9132359bd3980701bc510b4542d2db220dafd6b2ef5448286ef520cb59c71e` (3570964 bytes).
- Builder blob hashes (`git hash-object`): `build.py` `a4faa25af85facb64b956b372f6b528aafdd7ec1`, `check.py` `3d00541d258745461ab52b1b0cb4e1716a27a95d`, `on.py` `644a6c0857fbcc72562032b58d57aa113fee0641`.
- Python 3.12.10; git version 2.46.0.windows.1.

## Checks

151 versions of 9 acts read back from git on the day each took effect and on the day before: 0 mismatches. Trailers: 0 commits whose trailers git cannot parse. Health: 0 merge commits on main, 0 commit dates that go backwards, 0 commits dated after the build.

A second build from the same corpus into an empty folder gave identical hashes for all 128 history commits and 232 tags (history tip `11657bec4c683079fcac8cbe7d83c4b7380d648a`).

## Decisions made by hand

- Acts were chosen by what the archives hold: the Constitution of Kenya 2010 (1 expression), the Capital Markets Act (all 30 expressions) and the Tax Procedures Act 2015 (all 20). The Penal Code (Cap. 63) has only 3 archived expressions and the Data Protection Act 2019 2, so they were not taken.
- The Companies Act 2015 was tried and dropped: Kenya Law gives no single commencement date ("Commenced"; "Note: 6th November 2015— Parts 1 to 14, 23, 31, 32, 38, 40, 42, 1st Schedule and 6th Schedule; 15th June 2016—All other parts"), and lists the two commencement notices as amendments without versions of their own, so its first version could not be dated by when each Part took effect.
- The Employment Act 2007 was tried and dropped: 2 of its 11 expressions (2017-07-03, 2019-11-25) have no archived copy, so the changes of Act No. 19 of 2015 (in force 2017-07-03, as Kenya Law dates it) could only be dated a year late.
- Licence: Kenya Law's terms of use (s. 9) make only raw, unannotated source documents CC BY-NC 4.0, and need an explicit Licensing Agreement from NCLR for commercial redistribution and AI training. Every version is read from the Internet Archive's copy, for the configured acts only. No legal text was given to a model.
- Version dates are Kenya Law's expression dates. Laws.Africa's terminology guide (https://docs.laws.africa/getting-started/terminology-guide) says "Amendments to Principal works come into force on the Commencement date of the Amending work" and that the first point in time is "the work as originally published"; so an amendment's expression is dated by its commencement (in force), and an act's original expression by its publication, which is replaced by the commencement date the page states.
- Credits: a version whose History names exactly one amending law (and no consolidation) between it and the previous version is credited to that law for every provision that changed. Otherwise a provision is credited only to laws that Kenya Law's editorial note inside that provision links to; the rest are unexplained (publisher).
- Editorial notes (akn-remark) are left out of the text and used only as credit evidence, except where a provision has no other text (repealed or spent), where the note is the provision's whole printed content.
- Part, Chapter and Division headings are left out; each provision file starts with its own number and heading. Every other text of each version is in a provision file: this is checked per version (verification.json, fidelity).
- Constitution: the first version is dated 2010-08-27, the commencement date Kenya Law states ("Commenced on 27 August 2010 by Promulgation"), not 2010-09-03, the date of its expression (Gazette publication).
- Tax Procedures Act: the first version is dated 2016-01-19, the commencement date Kenya Law states ("Commenced on 19 January 2016 by Tax Procedures Act Commencement"), not 2015-12-24, the date of its expression (Gazette publication).
- Batch 2 acts were chosen among the most-used national Acts for which every point-in-time version Kenya Law lists is available: the Kenya Revenue Authority Act, the Excise Duty Act 2015, the Estate Duty Act, the Independent Electoral and Boundaries Commission Act 2011, the Central Bank of Kenya Act and the Alcoholic Drinks Control Act 2010.
- Batch 2 left out, because one or more of the versions Kenya Law lists was not available (their changes could only be dated late): the Value Added Tax Act 2013 (11 versions), the Retirement Benefits Act (7), the Proceeds of Crime and Anti-Money Laundering Act (3), the Employment Act 2007 (2017-07-03, 2019-11-25), the Public Finance Management Act 2012 (2), the Income Tax Act (2021-07-01, 2026-05-15) and the Export Processing Zones Act (2001-06-14).
- The Law of Succession Act was left out of batch 2: Kenya Law dates its first version 1972-11-17 (publication) but states it commenced on 1 July 1981, after six amending versions, so its versions before 1981 would not be in-force dates.
- Kenya Revenue Authority Act: the first version is dated 1995-07-01, the commencement date Kenya Law states ("Commenced on 1 July 1995 by Kenya Revenue Authority Act Commencement"), not 1995-06-09, the date of its expression (Gazette publication).
- Excise Duty Act: the first version is dated 2015-12-01, the commencement date Kenya Law states ("Commenced on 1 December 2015 by Excise Duty Act Commencement"), not 2015-11-13, the date of its expression (Gazette publication).
- Estate Duty Act: the first version is dated 1963-06-12, the commencement date Kenya Law states ("Commenced on 12 June 1963"), not 1963-08-13, the date of its expression (Gazette publication).
- Alcoholic Drinks Control Act: the first version is dated 2010-11-22, the commencement date Kenya Law states ("Commenced on 22 November 2010 by Alcoholic Drinks Control Act Commencement"), not 2010-09-10, the date of its expression (Gazette publication).

## What AI did and did not do

The scripts that read the sources and build this repository were written by Claude Code running Claude Opus 5.5 (`claude-opus-5-5`) under Lexifina's direction.

No model wrote, translated or corrected legal text. No model runs at build time. Every word of law in this repository comes from the official sources above.

The commit messages are written by `build.py` from the source data.

Model use at data-build time:
- Claude Code (Claude Opus 5.5, claude-opus-5-5) wrote the adapter and configuration and chose the acts. No model wrote, summarised or transformed legal text: the text is parsed by deterministic code.
- Claude Code (Claude Opus 5.5, claude-opus-5-5) wrote the adapter and configuration and chose the acts. No model wrote, summarised or transformed legal text: Lexifina's code is deterministic code.
