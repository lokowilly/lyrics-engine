import unittest
from unittest.mock import patch

from lyrics_engine import search_lyrics
from lyrics_engine.models import LyricsResult


class TestEngineLyricsCom(unittest.TestCase):

    @patch("lyrics_engine.engine.search_lyrics_com")
    @patch("lyrics_engine.engine.search_lyrics_lyricsweb")
    @patch("lyrics_engine.engine.search_lyrics_ovh")
    def test_lyrics_com_fallback_finds_lyrics(
        self,
        mock_ovh,
        mock_lyricsweb,
        mock_lyrics_com,
    ):
        mock_ovh.return_value = LyricsResult(
            status="NOT_FOUND",
            source="lyrics.ovh",
            message="HTTP 404",
        )

        mock_lyricsweb.return_value = LyricsResult(
            status="NOT_FOUND",
            source="LyricsWeb",
            message="No encontrada",
        )

        mock_lyrics_com.return_value = LyricsResult(
            status="FOUND",
            artist="Artista alternativo",
            title="Título alternativo",
            lyrics="Letras ficticias para la prueba",
            source="lyrics.com",
            message="Encontrado mediante Lyrics.com",
        )

        result = search_lyrics(
            "Artista de prueba",
            "Canción de prueba",
        )

        self.assertEqual(result.status, "FOUND")
        self.assertEqual(result.lyrics, "Letras ficticias para la prueba")
        self.assertEqual(result.artist, "Artista de prueba")
        self.assertEqual(result.title, "Canción de prueba")
        self.assertEqual(result.source, "lyrics.com")
        self.assertEqual(result.attempt, 1)

        mock_ovh.assert_called()
        mock_lyricsweb.assert_called_once()
        mock_lyrics_com.assert_called_once_with(
            "Artista de prueba",
            "Canción de prueba",
        )


if __name__ == "__main__":
    unittest.main()
