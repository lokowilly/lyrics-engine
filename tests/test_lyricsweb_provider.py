import unittest
from unittest.mock import patch

from lyrics_engine.providers.lyricsweb import search_lyrics_lyricsweb


class FakeResponse:
    status_code = 200

    text = """
    <html>
        <div id="lyrics-panel">
            Primera línea<br>
            Segunda línea<br/>
            <p>Tercera línea</p>
            <p>Cuarta &amp; última</p>
        </div>
    </html>
    """


class TestLyricsWebProvider(unittest.TestCase):

    @patch("lyrics_engine.providers.lyricsweb.requests.get")
    def test_extracts_lyrics(self, mock_get):

        mock_get.return_value = FakeResponse()

        result = search_lyrics_lyricsweb(
            "Steve Perry",
            "Against the Wall",
        )

        self.assertEqual(result.status, "FOUND")
        self.assertEqual(result.artist, "Steve Perry")
        self.assertEqual(result.title, "Against the Wall")
        self.assertEqual(result.source, "lyricsweb")

        self.assertEqual(
            result.lyrics,
            "Primera línea\n\n"
            "Segunda línea\n\n"
            "Tercera línea\n\n"
            "Cuarta & última",
        )

        mock_get.assert_called_once()

    @patch("lyrics_engine.providers.lyricsweb.requests.get")
    def test_http_error(self, mock_get):

        response = FakeResponse()
        response.status_code = 404
        mock_get.return_value = response

        result = search_lyrics_lyricsweb(
            "Steve Perry",
            "Against the Wall",
        )

        self.assertEqual(result.status, "NOT_FOUND")
        self.assertEqual(result.source, "lyricsweb")
        self.assertEqual(result.artist, "Steve Perry")
        self.assertEqual(result.title, "Against the Wall")


    @patch("lyrics_engine.providers.lyricsweb.requests.get")
    def test_continues_after_404_with_title_variant(self, mock_get):
        respuesta_404 = FakeResponse()
        respuesta_404.status_code = 404

        respuesta_correcta = FakeResponse()
        mock_get.side_effect = [respuesta_404, respuesta_correcta]

        result = search_lyrics_lyricsweb(
            "Simply Red",
            "A New Flame (2008 Remaster)",
        )

        self.assertEqual(result.status, "FOUND")
        self.assertEqual(result.source, "lyricsweb")
        self.assertEqual(mock_get.call_count, 2)


if __name__ == "__main__":
    unittest.main()
