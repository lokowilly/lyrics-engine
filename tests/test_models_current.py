#!/usr/bin/env python3

import unittest

from lyrics_engine import LyricsResult


class TestLyricsResult(unittest.TestCase):

    def test_result_found(self):
        result = LyricsResult(
            status="FOUND",
            artist="Steve Perry",
            title="She's Mine",
            lyrics="These are lyrics",
            source="lyrics.ovh",
            message="Encontrado",
            variant="sin_apostrofe",
            query_title="Shes Mine",
        )

        self.assertEqual(result.status, "FOUND")
        self.assertEqual(result.artist, "Steve Perry")
        self.assertEqual(result.title, "She's Mine")
        self.assertEqual(result.lyrics, "These are lyrics")
        self.assertEqual(result.source, "lyrics.ovh")
        self.assertEqual(result.message, "Encontrado")
        self.assertEqual(result.variant, "sin_apostrofe")
        self.assertEqual(result.query_title, "Shes Mine")

    def test_result_error(self):
        result = LyricsResult(
            status="ERROR",
            message="Error de conexión",
        )

        self.assertEqual(result.status, "ERROR")
        self.assertIsNone(result.artist)
        self.assertIsNone(result.title)
        self.assertIsNone(result.lyrics)
        self.assertIsNone(result.source)
        self.assertEqual(result.message, "Error de conexión")
        self.assertIsNone(result.variant)
        self.assertIsNone(result.query_title)


if __name__ == "__main__":
    unittest.main()
