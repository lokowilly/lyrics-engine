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


if __name__ == "__main__":
    unittest.main()
