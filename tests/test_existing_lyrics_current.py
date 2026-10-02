#!/usr/bin/env python3

import unittest
from pathlib import Path

from lyrics_engine import read_existing_lyrics


MP3 = Path.home() / "Descargas/Musica/1998 - Greatest Hits -Steve Perry/03 - She's Mine.mp3"


class TestExistingLyricsCurrent(unittest.TestCase):

    def test_existing_lyrics(self):
        self.assertTrue(
            MP3.exists(),
            f"No existe el MP3 de prueba: {MP3}"
        )

        result = read_existing_lyrics(MP3)

        self.assertEqual(len(result), 1)

        uslt = result[0]

        self.assertEqual(uslt.lang, "eng")
        self.assertEqual(uslt.desc, "Lyrics")
        self.assertTrue(uslt.text)
        self.assertGreater(len(uslt.text), 0)


if __name__ == "__main__":
    unittest.main()
