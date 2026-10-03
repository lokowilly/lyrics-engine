import unittest
from unittest.mock import patch

from providers.lyricsweb import search_lyrics_lyricsweb


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

    @patch("providers.lyricsweb.requests.get")
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

    @patch("providers.lyricsweb.requests.get")
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


if __name__ == "__main__":
    unittest.main()
