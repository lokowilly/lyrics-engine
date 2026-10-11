import unittest
from unittest.mock import patch

from lyrics_engine import search_lyrics
from lyrics_engine.models import LyricsResult


class FakeResponse:
    status_code = 200

    def json(self):
        return {
            "lyrics": "Primera línea\nSegunda línea"
        }


class TestLyricsOVHProvider(unittest.TestCase):

    @patch("providers.lyrics_ovh.requests.get")
    def test_finds_lyrics_from_lyrics_ovh(self, mock_get):

        mock_get.return_value = FakeResponse()

        result = search_lyrics(
            "Steve Perry",
            "She's Mine",
        )

        self.assertEqual(result.status, "FOUND")
        self.assertEqual(result.artist, "Steve Perry")
        self.assertEqual(result.title, "She's Mine")
        self.assertEqual(result.lyrics, "Primera línea\nSegunda línea")
        self.assertEqual(result.source, "lyrics.ovh")

        mock_get.assert_called()

    @patch("lyrics_engine.engine.search_lyrics_com")
    @patch("lyrics_engine.engine.search_lyrics_lyricsweb")
    @patch("lyrics_engine.engine.time.sleep")
    @patch("providers.lyrics_ovh.requests.get")
    def test_http_error_returns_not_found(
        self,
        mock_get,
        mock_sleep,
        mock_lyricsweb,
        mock_lyrics_com,
    ):

        response = FakeResponse()
        response.status_code = 404

        mock_get.return_value = response

        mock_lyricsweb.return_value = LyricsResult(
            status="NOT_FOUND",
            source="LyricsWeb",
            message="No encontrada en la prueba",
        )
        mock_lyrics_com.return_value = LyricsResult(
            status="NOT_FOUND",
            source="lyrics.com",
            message="No encontrada en la prueba",
        )

        result = search_lyrics(
            "Steve Perry",
            "She's Mine",
        )

        self.assertEqual(result.status, "NOT_FOUND")
        self.assertEqual(result.artist, "Steve Perry")
        self.assertEqual(result.title, "She's Mine")
        self.assertIsNone(result.source)

        mock_lyricsweb.assert_called()
        mock_lyrics_com.assert_called()
        mock_sleep.assert_called_once_with(1)

if __name__ == "__main__":
    unittest.main()
