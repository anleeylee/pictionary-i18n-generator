# -*- coding: utf-8 -*-
"""Tests for pictionary-i18n-generator. Run:

    python -m unittest discover -s tests -v
"""
import json
import re
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from i18n_generator import (  # noqa: E402
    LANGS,
    SITE,
    hreflang_tags,
    main,
    render_page,
    translate_word,
    translate_wordlist,
    verify_hreflang,
)

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


class TranslateTests(unittest.TestCase):
    def test_known_word(self):
        self.assertEqual(translate_word("cat", "es"), "gato")
        self.assertEqual(translate_word("cat", "de"), "Katze")
        self.assertEqual(translate_word("cat", "fr"), "chat")
        self.assertEqual(translate_word("cat", "pt"), "gato")

    def test_unknown_word_returns_none(self):
        self.assertIsNone(translate_word("zzzzyx", "es"))

    def test_case_insensitive(self):
        self.assertEqual(translate_word("Dog", "es"), "perro")

    def test_translate_wordlist_structure(self):
        wl = {"slug": "virtual-pictionary", "words": [
            {"word": "cat"}, {"word": "zzzzyx"}]}
        out = translate_wordlist(wl, "es")
        self.assertEqual(out["language"], "es")
        self.assertEqual(len(out["words"]), 2)
        self.assertEqual(out["words"][0]["word"], "gato")
        self.assertFalse(out["words"][0]["untranslated"])
        self.assertTrue(out["words"][1]["untranslated"])
        self.assertEqual(out["untranslated_count"], 1)

    def test_all_languages_present_in_table(self):
        for word, entry in TRANSLATIONS_ALL.items():
            self.assertEqual(len(entry), 4)
        for lang in LANGS:
            self.assertIn(translate_word("cat", lang), ("gato", "Katze",
                                                        "chat"))


# referenced below
import i18n_generator as m  # noqa: E402
TRANSLATIONS_ALL = m.TRANSLATIONS


class HreflangTests(unittest.TestCase):
    def test_group_has_all_languages(self):
        tags = hreflang_tags(f"{SITE}virtual-pictionary", "en")
        text = "\n".join(tags)
        for h in ["en"] + LANGS + ["x-default"]:
            self.assertIn(f'hreflang="{h}"', text)

    def test_localized_urls(self):
        tags = hreflang_tags(f"{SITE}virtual-pictionary", "en")
        self.assertIn(f'hreflang="es" href="{SITE}virtual-pictionary/es/"',
                      "\n".join(tags))


class PageTests(unittest.TestCase):
    def test_page_renders_full_head(self):
        wl = {"slug": "virtual-pictionary", "words": [{"word": "cat"}]}
        html = render_page(wl, "es", "virtual-pictionary")
        self.assertIn('lang="es"', html)
        self.assertIn('rel="canonical"', html)
        self.assertIn('hreflang="x-default"', html)
        self.assertIn("application/ld+json", html)
        self.assertIn("gato", html)

    def test_page_has_no_bare_urls(self):
        wl = {"slug": "virtual-pictionary", "words": [{"word": "dog"}]}
        html = render_page(wl, "de", "virtual-pictionary")
        result = verify_hreflang(html, f"{SITE}virtual-pictionary")
        self.assertEqual(result["bare_urls"], [])
        self.assertEqual(result["missing"], [])


class VerifyTests(unittest.TestCase):
    def test_detects_missing_hreflang(self):
        text = '<link rel="alternate" hreflang="en" ' \
               'href="https://pictionarywordgenerators.com/virtual-pictionary" />'
        result = verify_hreflang(text, f"{SITE}virtual-pictionary")
        self.assertFalse(result["ok"])
        self.assertIn("x-default", result["missing"])

    def test_detects_bare_url(self):
        text = ('<a href="https://pictionarywordgenerators.com/">ok</a> '
                'https://pictionarywordgenerators.com/virtual-pictionary '
                'bare')
        result = verify_hreflang(text, f"{SITE}virtual-pictionary")
        self.assertEqual(len(result["bare_urls"]), 1)


class CliTests(unittest.TestCase):
    def test_translate_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            code = main(["translate", "--input", str(EXAMPLES / "wordlist.json"),
                         "--out-dir", tmp])
            self.assertEqual(code, 0)
            manifest = json.loads((Path(tmp) / "i18n-manifest.json")
                                  .read_text(encoding="utf-8"))
            self.assertEqual(len(manifest["languages"]), 4)
            es = json.loads((Path(tmp) / "virtual-pictionary.es.json")
                            .read_text(encoding="utf-8"))
            self.assertEqual(len(es["words"]), 16)
            self.assertGreater(es["coverage_pct"], 90)

    def test_pages_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            code = main(["pages", "--input", str(EXAMPLES / "wordlist.json"),
                         "--slug", "virtual-pictionary", "--out-dir", tmp])
            self.assertEqual(code, 0)
            for lang in ["en"] + LANGS:
                self.assertTrue((Path(tmp) /
                                 f"virtual-pictionary.{lang}.html").exists())

    def test_verify_passes_good_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "ok.html"
            p.write_text(render_page(
                {"slug": "virtual-pictionary", "words": [{"word": "cat"}]},
                "fr", "virtual-pictionary"), encoding="utf-8")
            self.assertEqual(main(["verify", "--file", str(p)]), 0)

    def test_verify_fails_bad_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "bad.html"
            p.write_text("<html><body>no hreflang</body></html>",
                         encoding="utf-8")
            self.assertEqual(main(["verify", "--file", str(p)]), 1)


if __name__ == "__main__":
    unittest.main()
