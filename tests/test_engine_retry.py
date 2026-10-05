import unittest
from unittest.mock import patch

from lyrics_engine import search_lyrics
from lyrics_engine.models import LyricsResult


class TestEngineRetry(unittest.TestCase):

    @patch("lyrics_engine.engine.time.sleep")
    @patch("lyrics_engine.engine.generate_title_variants")
    @patch("lyrics_engine.engine.search_lyrics_lyricsweb")
    @patch("lyrics_engine.engine.search_lyrics_ovh")
    def test_retry_recovers_after_complete_search_failure(
        self,
        mock_ovh,
        mock_lyricsweb,
        mock_variants,
        mock_sleep,
    ):
        # Una sola variante para que el test no dependa
        # de la implementación interna de title_variants.py.
        mock_variants.return_value = [
            ("original", "Canción de prueba"),
        ]

        # Primera búsqueda completa → NOT_FOUND.
        # Segunda búsqueda completa → FOUND.
        mock_ovh.side_effect = [
            LyricsResult(
                status="NOT_FOUND",
                source="lyrics.ovh",
                message="HTTP 404",
            ),
            LyricsResult(
                status="FOUND",
                source="lyrics.ovh",
                lyrics="Estas son las letras",
            ),
        ]

        mock_lyricsweb.return_value = LyricsResult(
            status="NOT_FOUND",
            source="lyricsweb",
            message="HTTP 404",
        )

        result = search_lyrics(
            "Artista de prueba",
            "Canción de prueba",
        )

        self.assertEqual(result.status, "FOUND")
        self.assertEqual(
            result.lyrics,
            "Estas son las letras",
        )

        self.assertEqual(result.attempt, 2)


        # Debe haber dos búsquedas completas.
        self.assertEqual(
            mock_ovh.call_count,
            2,
        )
        mock_sleep.assert_called_once_with(1)

    @patch("lyrics_engine.engine.time.sleep")
    @patch("lyrics_engine.engine.generate_title_variants")
    @patch("lyrics_engine.engine.search_lyrics_lyricsweb")
    @patch("lyrics_engine.engine.search_lyrics_ovh")
    def test_retry_recovers_after_provider_error(
        self,
        mock_ovh,
        mock_lyricsweb,
        mock_variants,
        mock_sleep,
    ):
        # Una sola variante para que el test no dependa
        # de la implementación interna de title_variants.py.
        mock_variants.return_value = [
            ("original", "Canción de prueba"),
        ]

        # Primera búsqueda completa → ERROR.
        # Segunda búsqueda completa → FOUND.
        mock_ovh.side_effect = [
            LyricsResult(
                status="ERROR",
                source="lyrics.ovh",
                message="Error de conexión",
            ),
            LyricsResult(
                status="FOUND",
                source="lyrics.ovh",
                lyrics="Estas son las letras",
            ),
        ]

        mock_lyricsweb.return_value = LyricsResult(
            status="NOT_FOUND",
            source="lyricsweb",
            message="HTTP 404",
        )

        result = search_lyrics(
            "Artista de prueba",
            "Canción de prueba",
        )

        self.assertEqual(result.status, "FOUND")
        self.assertEqual(
            result.lyrics,
            "Estas son las letras",
        )

        self.assertEqual(result.attempt, 2)


        # También debe haber dos búsquedas completas.
        self.assertEqual(
            mock_ovh.call_count,
            2,
        )

        mock_sleep.assert_called_once_with(1)

if __name__ == "__main__":
    unittest.main()
