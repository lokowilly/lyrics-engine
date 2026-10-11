import unittest
from unittest.mock import Mock, patch

from lyrics_engine.providers.lyrics_com import search_lyrics_com


SEARCH_HTML = """
<a href="/lyric-lf/181218/Steve+Perry/Oh+Sherrie">Oh Sherrie</a>
<a href="/lyric-lf/181218/Steve+Perry/Oh+Sherrie">Oh Sherrie</a>
<a href="/lyric-lf/999999/Other+Artist/Other+Song">Other Song</a>
"""

DETAIL_HTML = """
<html>
    <h1 id="lyric-title-text">Oh Sherrie</h1>
    <h3 class="lyric-artist">Steve Perry</h3>
    <pre id="lyric-body-text">
Línea ficticia uno<br>
Línea ficticia dos
    </pre>
</html>
"""


def fake_response(html):
    response = Mock()
    response.status_code = 200
    response.text = html
    response.raise_for_status.return_value = None
    return response


class TestLyricsComSearch(unittest.TestCase):

    @patch("lyrics_engine.providers.lyrics_com.requests.get")
    def test_finds_song_and_removes_duplicate_urls(self, mock_get):
        mock_get.side_effect = [
            fake_response(SEARCH_HTML),
            fake_response(DETAIL_HTML),
        ]

        result = search_lyrics_com("Steve Perry", "Oh Sherrie")

        self.assertEqual(result.status, "FOUND")
        self.assertEqual(result.artist, "Steve Perry")
        self.assertEqual(result.title, "Oh Sherrie")
        self.assertEqual(result.source, "lyrics.com")
        self.assertEqual(mock_get.call_count, 2)

    @patch("lyrics_engine.providers.lyrics_com.requests.get")
    def test_returns_not_found_without_matching_candidate(self, mock_get):
        mock_get.return_value = fake_response(
            '<a href="/lyric-lf/999999/Other+Artist/Other+Song">'
            'Other Song</a>'
        )

        result = search_lyrics_com("Steve Perry", "Oh Sherrie")

        self.assertEqual(result.status, "NOT_FOUND")
        self.assertEqual(mock_get.call_count, 1)

    @patch("lyrics_engine.providers.lyrics_com.requests.get")
    def test_reports_search_connection_error(self, mock_get):
        import requests

        mock_get.side_effect = requests.ConnectionError()

        result = search_lyrics_com("Steve Perry", "Oh Sherrie")

        self.assertEqual(result.status, "ERROR")
        self.assertEqual(result.source, "lyrics.com")


if __name__ == "__main__":
    unittest.main()
