import unittest
from unittest.mock import Mock, patch

from lyrics_engine.providers.lrclib import search_lyrics_lrclib


def fake_response(status_code, data=None, headers=None):
    response = Mock()
    response.status_code = status_code
    response.headers = headers or {}
    response.json.return_value = data
    return response


class TestLRCLIBProvider(unittest.TestCase):

    @patch("lyrics_engine.providers.lrclib.requests.get")
    def test_finds_exact_match(self, mock_get):
        mock_get.return_value = fake_response(200, [{
            "artistName": "Steve Perry",
            "trackName": "Oh Sherrie",
            "plainLyrics": "Texto de prueba",
            "syncedLyrics": None,
        }])

        result = search_lyrics_lrclib("Steve Perry", "Oh Sherrie")

        self.assertEqual(result.status, "FOUND")
        self.assertEqual(result.source, "LRCLIB")
        self.assertEqual(result.lyrics, "Texto de prueba")
        mock_get.assert_called_once()

    @patch("lyrics_engine.providers.lrclib.requests.get")
    def test_rejects_wrong_title(self, mock_get):
        mock_get.return_value = fake_response(200, [{
            "artistName": "Steve Perry",
            "trackName": "Another Song",
            "plainLyrics": "Texto que no corresponde",
        }])

        result = search_lyrics_lrclib("Steve Perry", "Oh Sherrie")

        self.assertEqual(result.status, "NOT_FOUND")
        self.assertIsNone(result.lyrics)

    @patch("lyrics_engine.providers.lrclib.requests.get")
    def test_converts_synced_lyrics_to_plain_text(self, mock_get):
        mock_get.return_value = fake_response(200, [{
            "artistName": "Steve Perry",
            "trackName": "Oh Sherrie",
            "plainLyrics": None,
            "syncedLyrics": "[00:01.20]Primera línea\n[00:04.50]Segunda línea",
        }])

        result = search_lyrics_lrclib("Steve Perry", "Oh Sherrie")

        self.assertEqual(result.status, "FOUND")
        self.assertEqual(result.lyrics, "Primera línea\nSegunda línea")

    @patch("lyrics_engine.providers.lrclib.requests.get")
    def test_http_404_returns_not_found(self, mock_get):
        mock_get.return_value = fake_response(404)

        result = search_lyrics_lrclib("Artista", "Canción")

        self.assertEqual(result.status, "NOT_FOUND")

    @patch("lyrics_engine.providers.lrclib.requests.get")
    def test_http_503_returns_error(self, mock_get):
        mock_get.return_value = fake_response(503)

        result = search_lyrics_lrclib("Artista", "Canción")

        self.assertEqual(result.status, "ERROR")
        self.assertIn("503", result.message)

    @patch("lyrics_engine.providers.lrclib.requests.get")
    def test_http_429_returns_error_and_retry_after(self, mock_get):
        mock_get.return_value = fake_response(
            429,
            headers={"Retry-After": "3"},
        )

        result = search_lyrics_lrclib("Artista", "Canción")

        self.assertEqual(result.status, "ERROR")
        self.assertIn("Retry-After: 3", result.message)


    @patch("lyrics_engine.providers.lrclib.requests.get")
    def test_connection_error(self, mock_get):
        import requests

        mock_get.side_effect = requests.ConnectionError(
            "conexión de prueba"
        )

        result = search_lyrics_lrclib("Artista", "Canción")

        self.assertEqual(result.status, "ERROR")
        self.assertIn("ConnectionError", result.message)
        self.assertIsNone(result.lyrics)

    @patch("lyrics_engine.providers.lrclib.requests.get")
    def test_invalid_json(self, mock_get):
        response = Mock()
        response.status_code = 200
        response.headers = {}
        response.json.side_effect = ValueError("JSON de prueba")
        mock_get.return_value = response

        result = search_lyrics_lrclib("Artista", "Canción")

        self.assertEqual(result.status, "ERROR")
        self.assertIn("JSON inválida", result.message)
        self.assertIsNone(result.lyrics)


if __name__ == "__main__":
    unittest.main()
