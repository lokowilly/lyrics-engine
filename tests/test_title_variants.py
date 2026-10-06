#!/usr/bin/env python3

import unittest

from lyrics_engine.title_variants import generate_title_variants


class TestGenerateTitleVariants(unittest.TestCase):

    def test_shes_mine(self):
        result = generate_title_variants("She's Mine")

        self.assertEqual(
            result,
            [
                ("original", "She's Mine"),
                ("sin_apostrofe", "Shes Mine"),
            ],
        )

    def test_when_youre_in_love(self):
        result = generate_title_variants(
            "When You're In Love (For the First Time)"
        )

        self.assertEqual(
            result,
            [
                (
                    "original",
                    "When You're In Love (For the First Time)",
                ),
                (
                    "sin_apostrofe",
                    "When Youre In Love (For the First Time)",
                ),
                (
                    "sin_parentesis",
                    "When You're In Love",
                ),
                (
                    "sin_parentesis_sin_apostrofe",
                    "When Youre In Love",
                ),
            ],
        )

    def test_forever_right_or_wrong(self):
        result = generate_title_variants(
            "Forever Right Or Wrong (Love's Like a River)"
        )

        self.assertEqual(
            result,
            [
                (
                    "original",
                    "Forever Right Or Wrong (Love's Like a River)",
                ),
                (
                    "sin_apostrofe",
                    "Forever Right Or Wrong (Loves Like a River)",
                ),
                (
                    "sin_parentesis",
                    "Forever Right Or Wrong",
                ),
            ],
        )

    def test_dont_fight_it(self):
        result = generate_title_variants("Don't Fight It")

        self.assertEqual(
            result,
            [
                ("original", "Don't Fight It"),
                ("sin_apostrofe", "Dont Fight It"),
            ],
        )

    def test_remastered_2003(self):
        result = generate_title_variants(
            "Truth Hits Everybody (Remastered 2003)"
        )

        self.assertIn(
            ("sin_parentesis", "Truth Hits Everybody"),
            result,
        )

    def test_remaster_2008_preserves_title_parentheses(self):
        result = generate_title_variants(
            "Money's Too Tight (To Mention) (2008 Remaster)"
        )

        self.assertIn(
            (
                "sin_sufijo_editorial",
                "Money's Too Tight (To Mention)",
            ),
            result,
        )

    def test_bonus_track(self):
        result = generate_title_variants(
            "Baby, I Love You (bonus track)"
        )

        self.assertIn(
            "Baby, I Love You",
            [value for name, value in result],
        )

    def test_remaster_2005(self):
        result = generate_title_variants(
            "Sax and Violins (2005 Remaster)"
        )

        self.assertIn(
            (
                "sin_sufijo_editorial",
                "Sax and Violins",
            ),
            result,
        )

    def test_radio_mix(self):
        result = generate_title_variants(
            "Fake (- Radio Mix)"
        )

        self.assertIn(
            "Fake",
            [value for name, value in result],
        )

if __name__ == "__main__":
    unittest.main()
