#!/usr/bin/env python3

import unittest
from pathlib import Path

from lyrics_engine.metadata import get_metadata


MP3 = Path.home() / "Descargas/Musica/1998 - Greatest Hits -Steve Perry/03 - She's Mine.mp3"


class TestMetadataCurrent(unittest.TestCase):

    def test_metadata_real_mp3(self):
        self.assertTrue(
            MP3.exists(),
            f"No existe el MP3 de prueba: {MP3}"
        )

        result = get_metadata(MP3)

        self.assertEqual(result.status, "OK")
        self.assertEqual(result.artist, "Steve Perry")
        self.assertEqual(result.title, "She's Mine")

        self.assertIsNone(result.lyrics)
        self.assertIsNone(result.source)
        self.assertIsNone(result.message)


if __name__ == "__main__":
    unittest.main()
