# Pictionary I18N Generator

> **Multilingual generator for a Pictionary word site — translates word libraries and content pages into Spanish, German, French and Portuguese, and outputs complete hreflang alternate groups so every language variant is correctly linked for search engines. Standard library only.**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![CLI](https://img.shields.io/badge/CLI-ready-4B8BBE)](i18n_generator.py)
[![No dependencies](https://img.shields.io/badge/deps-stdlib%20only-blueviolet)](requirements.txt)

---

## Links

- 🎲 **Try the live tool:** [Pictionary Word Generator — 7,000+ free drawing prompts](https://pictionarywordgenerators.com/)
- 🕹️ **Play online:** [Virtual Pictionary — play with friends in your browser](https://pictionarywordgenerators.com/virtual-pictionary)
- Read the Chinese version: [README.zh-CN.md](README.zh-CN.md)

---

## What it does

A content site that only exists in English leaves most of the web on the
table. Localizing the word libraries and the theme pages opens up the
Spanish, German, French and Portuguese markets — but only if search engines
can tell the variants apart. That is what hreflang is for, and getting a
group wrong (missing a language, missing `x-default`, or a broken alternate
URL) can suppress every variant in the index.

This tool automates both halves:

1. **`translate`** — translate a word-library JSON into per-language JSON
   files (`es` / `de` / `fr` / `pt`) with an offline dictionary table,
   per-word coverage flags and an `i18n-manifest.json` summary. Fully
   deterministic, no API keys, nothing leaves your machine.
2. **`pages`** — render language-aware HTML pages (word list + generator
   embed + FAQ) with a **complete hreflang alternate group** (English +
   all 4 languages + `x-default`), canonical URL, Open Graph and JSON-LD
   WebPage schema. The multilingual title / description / FAQ copy ships
   in the built-in `PAGE_COPY` table.
3. **`verify`** — check any rendered page: every language present in the
   hreflang group, `x-default` present, and zero bare site URLs (JSON-LD
   and attribute URLs excluded). CI-friendly, exits non-zero on failure.

The built-in dictionary covers 49 everyday Pictionary words across all four
languages; words outside the table are kept in English and flagged
`untranslated` with a coverage percentage, so you always know what a
professional translator still needs to review.

## Why it matters

This is the localization layer on top of the rest of the toolkit:
[Pictionary Wordlist Generator](https://github.com/anleeylee/pictionary-wordlist-generator)
creates the libraries, [Pictionary Page Generator](https://github.com/anleeylee/pictionary-page-generator)
builds the English pages, [Pictionary SEO Scanner](https://github.com/anleeylee/pictionary-seo-scanner)
keeps on-page SEO healthy, [Pictionary Keyword Tracker](https://github.com/anleeylee/pictionary-keyword-tracker)
decides what to build next, [Pictionary GSC Monitor](https://github.com/anleeylee/pictionary-gsc-monitor)
tracks indexing and [Pictionary Link Matrix](https://github.com/anleeylee/pictionary-link-matrix)
grows the backlink profile. This tool ships the same pages and word lists
in four more languages — with hreflang groups that Google can trust.

## Install

```bash
git clone https://github.com/anleeylee/pictionary-i18n-generator.git
cd pictionary-i18n-generator

# standard library only — no pip install needed
python i18n_generator.py --help
```

## Usage

```bash
# 1. translate a word library into es / de / fr / pt JSON + manifest
python i18n_generator.py translate \
  --input examples/wordlist.json --out-dir out

# 2. render multilingual HTML pages with full hreflang groups
python i18n_generator.py pages \
  --input examples/wordlist.json --slug virtual-pictionary --out-dir out

# 3. hygiene gate (CI-friendly, exits non-zero on problems)
python i18n_generator.py verify \
  --file out/virtual-pictionary.es.html
```

### Output

- `<slug>.{es,de,fr,pt}.json` + `i18n-manifest.json` — per-language word
  libraries with coverage stats
- `<slug>.{en,es,de,fr,pt}.html` — language-aware pages: hreflang group,
  canonical, Open Graph, JSON-LD schema, translated word list and FAQ

## Tests

```bash
python -m unittest discover -s tests -v
```

Covers dictionary lookups (known / unknown / case-insensitive / all 4
languages), wordlist translation structure and coverage flags, complete
hreflang groups with localized URLs, rendered-page head completeness,
bare-URL detection with script/attribute exemption, and full CLI runs.
15 tests, all offline.

## License

MIT — use it, extend it, keep the attribution. The dictionary table is
yours to grow; the generated pages are yours to publish.
