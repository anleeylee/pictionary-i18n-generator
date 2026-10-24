# -*- coding: utf-8 -*-
"""pictionary-i18n-generator — multilingual generator for a Pictionary word site.

Translates Pictionary word libraries and content pages into Spanish,
German, French and Portuguese, and outputs hreflang alternate links so
every language variant is discoverable and correctly linked for search
engines. Standard library only — the built-in dictionary table keeps
translation fully offline and deterministic.

Subcommands:
    translate   Translate a word-library JSON into per-language JSON files
                (es / de / fr / pt) plus a summary manifest.
    pages       Render multilingual HTML pages (word list + generator embed +
                FAQ) with full hreflang alternate groups, canonical URLs,
                Open Graph and JSON-LD schema.
    verify      Check that a rendered page has a complete hreflang group
                (one group, every language present, x-default present) and
                no bare site URLs.

Examples:
    python i18n_generator.py translate --input examples/wordlist.json --out-dir out
    python i18n_generator.py pages --input examples/wordlist.json --slug virtual-pictionary --out-dir out
    python i18n_generator.py verify --file out/virtual-pictionary.es.html
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

SITE = "https://pictionarywordgenerators.com/"
HOMEPAGE = "https://pictionarywordgenerators.com/"
LANGS = ["es", "de", "fr", "pt"]

LANG_NAMES = {
    "en": "English",
    "es": "Español",
    "de": "Deutsch",
    "fr": "Français",
    "pt": "Português",
}

# Built-in offline dictionary table: english -> es / de / fr / pt.
TRANSLATIONS = {
    "cat": ("gato", "Katze", "chat", "gato"),
    "dog": ("perro", "Hund", "chien", "cachorro"),
    "house": ("casa", "Haus", "maison", "casa"),
    "tree": ("árbol", "Baum", "arbre", "árvore"),
    "car": ("coche", "Auto", "voiture", "carro"),
    "book": ("libro", "Buch", "livre", "livro"),
    "sun": ("sol", "Sonne", "soleil", "sol"),
    "moon": ("luna", "Mond", "lune", "lua"),
    "star": ("estrella", "Stern", "étoile", "estrela"),
    "fish": ("pez", "Fisch", "poisson", "peixe"),
    "bird": ("pájaro", "Vogel", "oiseau", "pássaro"),
    "flower": ("flor", "Blume", "fleur", "flor"),
    "apple": ("manzana", "Apfel", "pomme", "maçã"),
    "banana": ("plátano", "Banane", "banane", "banana"),
    "hat": ("sombrero", "Hut", "chapeau", "chapéu"),
    "shoe": ("zapato", "Schuh", "chaussure", "sapato"),
    "clock": ("reloj", "Uhr", "horloge", "relógio"),
    "phone": ("teléfono", "Telefon", "téléphone", "telefone"),
    "camera": ("cámara", "Kamera", "appareil photo", "câmera"),
    "guitar": ("guitarra", "Gitarre", "guitare", "violão"),
    "piano": ("piano", "Klavier", "piano", "piano"),
    "airplane": ("avión", "Flugzeug", "avion", "avião"),
    "bicycle": ("bicicleta", "Fahrrad", "vélo", "bicicleta"),
    "boat": ("barco", "Boot", "bateau", "barco"),
    "train": ("tren", "Zug", "train", "trem"),
    "mountain": ("montaña", "Berg", "montagne", "montanha"),
    "ocean": ("océano", "Ozean", "océan", "oceano"),
    "beach": ("playa", "Strand", "plage", "praia"),
    "snowman": ("muñeco de nieve", "Schneemann", "bonhomme de neige",
                "boneco de neve"),
    "birthday": ("cumpleaños", "Geburtstag", "anniversaire", "aniversário"),
    "christmas": ("navidad", "Weihnachten", "Noël", "Natal"),
    "halloween": ("halloween", "Halloween", "Halloween", "Halloween"),
    "rocket": ("cohete", "Rakete", "fusée", "foguete"),
    "robot": ("robot", "Roboter", "robot", "robô"),
    "pizza": ("pizza", "Pizza", "pizza", "pizza"),
    "umbrella": ("paraguas", "Regenschirm", "parapluie", "guarda-chuva"),
    "rainbow": ("arcoíris", "Regenbogen", "arc-en-ciel", "arco-íris"),
    "elephant": ("elefante", "Elefant", "éléphant", "elefante"),
    "tiger": ("tigre", "Tiger", "tigre", "tigre"),
    "lion": ("león", "Löwe", "lion", "leão"),
    "monkey": ("mono", "Affe", "singe", "macaco"),
    "spider": ("araña", "Spinne", "araignée", "aranha"),
    "butterfly": ("mariposa", "Schmetterling", "papillon", "borboleta"),
    "bee": ("abeja", "Biene", "abeille", "abelha"),
    "frog": ("rana", "Frosch", "grenouille", "sapo"),
    "duck": ("pato", "Ente", "canard", "pato"),
    "penguin": ("pingüino", "Pinguin", "manchot", "pinguim"),
    "shark": ("tiburón", "Hai", "requin", "tubarão"),
    "whale": ("ballena", "Wal", "baleine", "baleia"),
}

# Multilingual page copy (title / meta description / generator embed / FAQ).
PAGE_COPY = {
    "en": {
        "title_tpl": "{name} — Free Pictionary Words & Generator",
        "desc_tpl": "Play {name} online: thousands of free drawing prompts, "
                    "difficulty filters, printable lists and a live shuffle "
                    "mode. No sign-up needed.",
        "faq": [
            ("How do I play Pictionary online?",
             "Open the generator, pick a difficulty, and draw or guess the "
             "prompt. The built-in timer and shuffle mode keep rounds "
             "moving."),
            ("Can I print the word lists?",
             "Yes — every list has a print-friendly view with large text "
             "for cards."),
        ],
    },
    "es": {
        "title_tpl": "{name} — Palabras de Pictionary y Generador Gratis",
        "desc_tpl": "Juega {name} en línea: miles de ideas de dibujo gratis, "
                    "filtros de dificultad, listas imprimibles y modo "
                    "aleatorio. Sin registro.",
        "faq": [
            ("¿Cómo juego a Pictionary en línea?",
             "Abre el generador, elige una dificultad y dibuja o adivina la "
             "palabra. El temporizador y el modo aleatorio mantienen el "
             "ritmo."),
            ("¿Puedo imprimir las listas de palabras?",
             "Sí — cada lista tiene una vista imprimible con texto grande "
             "para las tarjetas."),
        ],
    },
    "de": {
        "title_tpl": "{name} — Kostenlose Pictionary-Wörter und Generator",
        "desc_tpl": "Spiele {name} online: tausende kostenlose Zeichenideen, "
                    "Schwierigkeitsfilter, druckbare Listen und ein Live-"
                    "Mischmodus. Keine Anmeldung nötig.",
        "faq": [
            ("Wie spiele ich Pictionary online?",
             "Öffne den Generator, wähle einen Schwierigkeitsgrad und zeichne "
             "oder rate den Begriff. Timer und Mischmodus halten die Runde "
             "in Bewegung."),
            ("Kann ich die Wortlisten drucken?",
             "Ja — jede Liste hat eine druckfreundliche Ansicht mit großem "
             "Text für Karten."),
        ],
    },
    "fr": {
        "title_tpl": "{name} — Mots de Pictionary et Générateur Gratuits",
        "desc_tpl": "Jouez à {name} en ligne : des milliers d'idées de dessin "
                    "gratuites, des filtres de difficulté, des listes "
                    "imprimables et un mode mélange en direct. Sans "
                    "inscription.",
        "faq": [
            ("Comment jouer à Pictionary en ligne ?",
             "Ouvrez le générateur, choisissez une difficulté et dessinez ou "
             "devinez le mot. Le minuteur et le mode mélange rythment la "
             "partie."),
            ("Puis-je imprimer les listes de mots ?",
             "Oui — chaque liste a un affichage imprimable avec du texte "
             "grand pour les cartes."),
        ],
    },
    "pt": {
        "title_tpl": "{name} — Palavras de Pictionary e Gerador Grátis",
        "desc_tpl": "Jogue {name} online: milhares de ideias de desenho "
                    "grátis, filtros de dificuldade, listas imprimíveis e "
                    "modo aleatório ao vivo. Sem cadastro.",
        "faq": [
            ("Como jogar Pictionary online?",
             "Abra o gerador, escolha uma dificuldade e desenhe ou adivinhe "
             "a palavra. O cronômetro e o modo aleatório mantêm o ritmo."),
            ("Posso imprimir as listas de palavras?",
             "Sim — cada lista tem uma visualização imprimível com texto "
             "grande para cartões."),
        ],
    },
}


def translate_word(word: str, lang: str) -> str | None:
    """Return the translation of a lowercased english word, or None."""
    if lang == "en" or lang not in LANGS:
        return word
    entry = TRANSLATIONS.get(word.lower())
    if not entry:
        return None
    return entry[LANGS.index(lang)]


def _word_name(word: str, lang: str) -> str:
    tr = translate_word(word, lang)
    return tr if tr else word


def translate_wordlist(wordlist: dict, lang: str) -> dict:
    """Translate one word library into one language (JSON-safe)."""
    translated = {"slug": wordlist.get("slug", "wordlist"),
                  "language": lang,
                  "source_language": wordlist.get("language", "en"),
                  "title": wordlist.get("title", ""),
                  "words": []}
    untranslated = 0
    for item in wordlist.get("words", []):
        word = item.get("word", "")
        tr = translate_word(word, lang)
        entry = dict(item)
        entry["word"] = tr if tr else word
        entry["original_word"] = word
        entry["untranslated"] = tr is None
        if tr is None:
            untranslated += 1
        translated["words"].append(entry)
    translated["untranslated_count"] = untranslated
    translated["coverage_pct"] = round(
        100 * (1 - untranslated / max(len(translated["words"]), 1)), 1)
    return translated


# --------------------------------------------------------------------------- #
# hreflang
# --------------------------------------------------------------------------- #
def hreflang_tags(base_url: str, lang: str) -> list[str]:
    """Build the hreflang alternate group for one page (all languages)."""
    tags = [f'<link rel="alternate" hreflang="en" href="{base_url}" />']
    for other in LANGS:
        href = _localized_url(base_url, other)
        tags.append(f'<link rel="alternate" hreflang="{other}" '
                    f'href="{href}" />')
    tags.append(f'<link rel="alternate" hreflang="x-default" '
                f'href="{base_url}" />')
    return tags


def _localized_url(base_url: str, lang: str) -> str:
    if lang == "en":
        return base_url
    return base_url.rstrip("/") + f"/{lang}/"


# --------------------------------------------------------------------------- #
# Page rendering
# --------------------------------------------------------------------------- #
def render_page(wordlist: dict, lang: str, slug: str,
                base_url: str | None = None) -> str:
    """Render one multilingual HTML page for the site's {slug} page."""
    if base_url is None:
        base_url = f"{SITE}{slug}"
    name = PAGE_COPY["en"]["title_tpl"].format(
        name=slug.replace("-", " ").title()).split(" — ")[0]
    copy = PAGE_COPY.get(lang, PAGE_COPY["en"])
    title = copy["title_tpl"].format(name=name)
    description = copy["desc_tpl"].format(name=name)
    canonical = base_url if lang == "en" else _localized_url(base_url, lang)
    alternates = "\n    ".join(hreflang_tags(base_url, lang))
    words = wordlist.get("words", [])
    word_items = "\n      ".join(
        f"<li>{_word_name(w.get('word', ''), lang)}"
        + (" <em>(untranslated)</em>" if translate_word(
            w.get("word", ""), lang) is None else "")
        + "</li>"
        for w in words)
    faq_items = "\n      ".join(
        f'<h3>{q}</h3><p>{a}</p>' for q, a in copy["faq"])
    schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "description": description,
        "url": canonical,
        "inLanguage": lang,
        "isPartOf": {"@type": "WebSite", "name": "Pictionary Word Generator",
                     "url": SITE},
    }, ensure_ascii=False)
    html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <link rel="canonical" href="{canonical}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="{canonical}">
  {alternates}
  <script type="application/ld+json">{schema}</script>
</head>
<body>
  <header>
    <a href="{SITE}">Pictionary Word Generator</a>
  </header>
  <main>
    <h1>{title}</h1>
    <section class="generator">
      <a class="btn" href="{SITE}">Open the free generator</a>
    </section>
    <section class="words">
      <h2>Sample words</h2>
      <ul>
      {word_items}
      </ul>
    </section>
    <section class="faq">
      <h2>FAQ</h2>
      {faq_items}
    </section>
  </main>
  <footer>
    <a href="{SITE}">Free Pictionary Word Generator</a>
  </footer>
</body>
</html>
"""
    return html


# --------------------------------------------------------------------------- #
# Verification
# --------------------------------------------------------------------------- #
def verify_hreflang(text: str, base_url: str) -> dict:
    """Check a rendered page: hreflang group complete, no bare site URLs."""
    expected = ["en"] + LANGS + ["x-default"]
    found = {m.group(1): m.group(2)
             for m in re.finditer(r'hreflang="([^"]+)" href="([^"]+)"',
                                  text)}
    missing = [h for h in expected if h not in found]
    # Strip <script> blocks (JSON-LD) and <a>/<link> href values, then scan
    # for any remaining bare site URL.
    no_script = re.sub(r"<script.*?</script>", "", text, flags=re.DOTALL)
    no_attrs = re.sub(r'(?:href|content)="https?://[^"]+"', "", no_script)
    bare = re.findall(
        r"https?://pictionarywordgenerators\.com[^\s\"'>)]*", no_attrs)
    ok = not missing and not bare and "x-default" in found
    return {"missing": missing, "bare_urls": bare, "ok": ok}


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _load_wordlist(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, dict) and "words" in data:
        return data
    if isinstance(data, list):
        return {"slug": "wordlist", "language": "en", "title": "Word list",
                "words": data}
    raise ValueError(f"unrecognized wordlist format in {path}")


def cmd_translate(args: argparse.Namespace) -> int:
    wordlist = _load_wordlist(args.input)
    os.makedirs(args.out_dir, exist_ok=True)
    manifest = {"source": args.input, "slug": wordlist.get("slug", "wordlist"),
                "languages": {}}
    for lang in LANGS:
        out = translate_wordlist(wordlist, lang)
        path = os.path.join(args.out_dir,
                            f"{wordlist.get('slug', 'wordlist')}.{lang}.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=2)
        manifest["languages"][lang] = {
            "file": os.path.basename(path),
            "words": len(out["words"]),
            "untranslated": out["untranslated_count"],
            "coverage_pct": out["coverage_pct"],
        }
    with open(os.path.join(args.out_dir, "i18n-manifest.json"), "w",
              encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
    print(f"Translated {wordlist.get('slug', 'wordlist')} into "
          f"{len(LANGS)} languages -> {args.out_dir}/")
    for lang, info in manifest["languages"].items():
        print(f"  {lang}: {info['words']} words, "
              f"{info['coverage_pct']}% covered")
    return 0


def cmd_pages(args: argparse.Namespace) -> int:
    wordlist = _load_wordlist(args.input)
    os.makedirs(args.out_dir, exist_ok=True)
    base_url = f"{SITE}{args.slug}"
    for lang in ["en"] + LANGS:
        html = render_page(wordlist, lang, args.slug, base_url)
        path = os.path.join(args.out_dir, f"{args.slug}.{lang}.html")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html)
    print(f"Rendered {len(['en'] + LANGS)} language pages for /{args.slug} "
          f"-> {args.out_dir}/")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    with open(args.file, "r", encoding="utf-8") as fh:
        text = fh.read()
    result = verify_hreflang(text, args.base_url)
    print("missing hreflang:", result["missing"] if result["missing"] else "NONE")
    print("bare URLs:", result["bare_urls"] if result["bare_urls"] else "NONE")
    print("hreflang:", "OK" if result["ok"] else "FAIL")
    return 0 if result["ok"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="i18n_generator.py",
        description="Multilingual generator for a Pictionary word site — "
                    "translates word libraries and pages into Spanish, "
                    "German, French and Portuguese with hreflang output.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("translate", help="translate a word library")
    p.add_argument("--input", required=True)
    p.add_argument("--out-dir", required=True)
    p.set_defaults(func=cmd_translate)

    p = sub.add_parser("pages", help="render multilingual HTML pages")
    p.add_argument("--input", required=True)
    p.add_argument("--slug", required=True,
                   help="target page slug, e.g. virtual-pictionary")
    p.add_argument("--out-dir", required=True)
    p.set_defaults(func=cmd_pages)

    p = sub.add_parser("verify", help="verify hreflang and URL hygiene")
    p.add_argument("--file", required=True)
    p.add_argument("--base-url", default=f"{SITE}virtual-pictionary")
    p.set_defaults(func=cmd_verify)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
