
import shutil
import tempfile
import unittest
from pathlib import Path

from mutagen.flac import FLAC

from lyrics_engine.writer import write_lyrics


SOURCE_FLAC = Path(
    "/home/willy/Descargas/Musica/"
    "Reservoir Dogs Soundtrack [FLAC+MP3]"
    "(Big Papi) With Dialog Excerpts 1992/"
    "08 Lawrence Tierney - Madonna Speech.flac"
)


class TestWriterFLAC(unittest.TestCase):
    def test_write_lyrics_and_create_backup(self):
        self.assertTrue(
            SOURCE_FLAC.is_file(),
            f"No existe el FLAC de prueba: {SOURCE_FLAC}",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            test_flac = Path(tmpdir) / "test.flac"
            shutil.copy2(SOURCE_FLAC, test_flac)

            result = write_lyrics(
                test_flac,
                "LETRA FLAC DE PRUEBA",
            )

            self.assertEqual(result.status, "WRITTEN")

            audio = FLAC(test_flac)
            self.assertEqual(
                audio.get("LYRICS"),
                ["LETRA FLAC DE PRUEBA"],
            )

            backup = test_flac.with_suffix(".flac.bak")
            self.assertTrue(backup.is_file())

    def test_does_not_overwrite_existing_lyrics(self):
        self.assertTrue(SOURCE_FLAC.is_file())

        with tempfile.TemporaryDirectory() as tmpdir:
            test_flac = Path(tmpdir) / "test.flac"
            shutil.copy2(SOURCE_FLAC, test_flac)

            audio = FLAC(test_flac)
            audio["LYRICS"] = ["LETRA ORIGINAL"]
            audio.save()

            result = write_lyrics(
                test_flac,
                "LETRA NUEVA",
                overwrite=False,
            )

            self.assertEqual(result.status, "ALREADY_EXISTS")

            audio_after = FLAC(test_flac)
            self.assertEqual(
                audio_after.get("LYRICS"),
                ["LETRA ORIGINAL"],
            )


if __name__ == "__main__":
    unittest.main()
