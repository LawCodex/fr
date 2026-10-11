# France — LawCodex

French legislation currently in force, as plain Markdown: the Constitution and the texts of the
*bloc de constitutionnalité*, every consolidated code, and every consolidated loi, loi organique,
ordonnance, décret-loi and décret that the official LEGI database marks as in force.

- **Jurisdiction:** France (`fr`)
- **Language:** French (sole official language)
- **Consolidation date:** 2026-10-11 (LEGI global dump of 2025-07-13 + every daily increment up to 2026-10-10 (`LEGI_20261010-211641`))
- **Retrieved:** 2026-10-11

## Contents

| Category | Directory | Texts | Articles in force |
|---|---|---:|---:|
| Constitution, Déclaration de 1789, Préambule de 1946, Constitution de 1848 (residual), lois constitutionnelles | `constitution/` | 13 | 148 |
| Codes (76 codes; 14 large ones split per partie/livre) | `codes/` | 76 | 165,279 |
| Lois (incl. 80 lois organiques) | `lois/` | 2,800 | 27,985 |
| Ordonnances (1539 – 2026) | `ordonnances/` | 1,316 | 7,154 |
| Décrets-lois (1924 – 1940) | `decrets-lois/` | 12 | 73 |
| Décrets | `decrets/` | 44,672 | 176,093 |
| **Total** | | **48,889** | **376,732** |

Each file has a YAML front matter (`title`, `identifier` = LEGITEXT id, `cid` = JORFTEXT id,
`nature`, `number`, `nor`, `type`, `date` = signature date, `last_amended` = date of last
modification recorded by LEGI, `consolidated`, `status`, `source` = Légifrance URL, `retrieved`)
followed by the text. The internal hierarchy of each text (partie / livre / titre / chapitre /
section …) is mapped to Markdown headings, each article being a heading (`## Article 1`,
`### Article L. 110-1` …); below heading level 6, section titles and article labels are bold.
Article notes (*Nota*) are kept as block quotes. The *visas* (preamble formula) and the
signatories are kept for lois, ordonnances and décrets. Simple tables are converted to Markdown
tables; tables with merged cells are kept as cleaned HTML.

## Structure

```
constitution/
  constitution-du-4-octobre-1958.md            Constitution of the Fifth Republic
  declaration-du-26-aout-1789.md               Déclaration des droits de l'homme et du citoyen
  constitution-du-27-octobre-1946.md           Préambule de 1946 (the only part still in force)
  constitution-du-4-novembre-1848.md           the few articles LEGI still marks as in force
  lois-constitutionnelles/                     constitutional laws with provisions of their own still
                                               in force (incl. loi constitutionnelle 2005-205, whose
                                               article 2 is the Charte de l'environnement)
codes/
  <code>.md                                    one file per code …
  <code>/index.md + NN-<partie-or-livre>.md     … or, for codes over 4 MB, one file per top-level
                                               part (partie / livre), split again one level down
                                               if a part exceeds 12 MB
lois/<year>/<slug>.md                          lois, lois organiques, lois de programme
ordonnances/<year>/<slug>.md
decrets-lois/<year>/<slug>.md
decrets/<year>/[<month>/]<slug>.md             years with more than 900 décrets are split by month
                                               (GitHub lists at most 1,000 entries per directory)
```

`<year>` is the year of signature of the text (`date` in the front matter). File names are
ASCII slugs of the full official title, truncated at ~95 characters.

## What is NOT included

- **Arrêtés** (ministerial / prefectoral orders): ~69,700 in force in LEGI — mass-volume
  secondary legislation, skipped.
- Other minor natures present in LEGI: délibérations, décisions, avis, circulaires,
  conventions, accords de la fonction publique (135 texts in total) — skipped.
- **Repealed / historical versions**: only the version in force at the consolidation date is
  given (git history will track future changes). Articles whose entry into force is deferred
  to a later date are not included until that date.
- Texts that LEGI keeps "in force" but that no longer contain any article in force (typically
  amending laws whose provisions have all been codified or spent) are omitted:
  257 lois, 26 lois organiques, 4 ordonnances, 140 décrets and 10 lois constitutionnelles.
- Texts not consolidated by DILA at all (e.g. most texts only published in the *Journal
  officiel* — JORF database — and never consolidated in LEGI), collective agreements (KALI),
  case law, EU law.
- 236 structure links (out of ~377,000) point to article versions that are not
  present in the in-force part of the dump (inconsistencies in the source data); those articles
  are missing.

## Source and licence

- Source: **LEGI** database of the Direction de l'information légale et administrative (DILA),
  open-data bulk dump: <https://echanges.dila.gouv.fr/OPENDATA/LEGI/> (also listed on
  <https://www.data.gouv.fr/fr/datasets/legi-codes-lois-et-reglements-consolides/>). The same
  data powers <https://www.legifrance.gouv.fr>; each file's `source` links to the Légifrance page.
- Licence of the source data: **Licence Ouverte / Open Licence v2.0** (Etalab),
  <https://www.etalab.gouv.fr/licence-ouverte-open-licence/>. Official legislative texts are
  furthermore not protected by copyright in France (art. L. 122-5 CPI and settled case law on
  official acts). Attribution: « Source : DILA — base LEGI, Légifrance ».
- This is **not** an official publication. Only the *Journal officiel* is authentic; consult
  Légifrance for legally binding versions.

## Regenerating

Requires Python 3 with `requests` and `lxml` (`scripts/requirements.txt`).

```sh
RAW=../_raw/fr                                   # scratch dir, NOT committed (~3 GB)
python scripts/fetch.py $RAW/dl                  # latest global dump + all daily increments
python scripts/ingest.py $RAW/dl $RAW/legi.db    # streams the tarballs into SQLite (no extraction)
python scripts/build.py $RAW/legi.db . --date $(date +%F)
scripts/publish.sh                               # commit + push in batches
```

- `fetch.py` downloads the newest `Freemium_legi_global_*.tar.gz` and every later
  `LEGI_*.tar.gz` increment (cached; ≤ 4 connections; descriptive User-Agent).
- `ingest.py` reads the tarballs as streams, keeps only the `code_et_TNC_en_vigueur` tree,
  applies the increments in order (including `liste_suppression_legi.dat` deletions) and stores
  texts, structures, sections and in-force article versions in SQLite (arrêtés' bodies skipped).
- `build.py` walks each text's structure (`STRUCT` → `SECTION_TA` → `LIEN_ART`), keeping the
  links whose validity interval contains the consolidation date, and renders Markdown
  (`htmlmd.py` converts the article HTML). It also writes `scripts/stats-*.json` with counts.
