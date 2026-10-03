#!/usr/bin/env python3

import tempfile
import unittest
from pathlib import Path

from mutagen.id3 import ID3, USLT

from lyrics_engine.writer import write_lyrics


class TestWriterProtectionCurrent(unittest.TestCase):

    def test_does_not_overwrite_existing_lyrics(self):
        with tempfile.TemporaryDirectory() as tmpdir:

            mp3 = Path(tmpdir) / "test.mp3"

            # Crear un archivo mínimo con tags ID3.
            audio = ID3()
            audio.add(
                USLT(
                    encoding=3,
                    lang="eng",
                    desc="Lyrics",
                    text="LETRA ORIGINAL",
                )
            )
            audio.save(mp3, v2_version=3)

            # Intentar escribir sin overwrite.
            result = write_lyrics(
                mp3,
                "LETRA NUEVA",
                overwrite=False,
            )

            self.assertEqual(
                result.status,
                "ALREADY_EXISTS",
            )

            # Verificar que la letra original sigue intacta.
            audio_after = ID3(mp3)
            uslt = audio_after.getall("USLT")

            self.assertEqual(len(uslt), 1)
            self.assertEqual(uslt[0].text, "LETRA ORIGINAL")


if __name__ == "__main__":
    unittest.main()
