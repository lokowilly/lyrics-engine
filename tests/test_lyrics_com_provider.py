import unittest

from lyrics_engine.providers.lyrics_com import parse_lyrics_page


SAMPLE_HTML = """
<html>
    <h1 id="lyric-title-text">Canción de prueba</h1>
    <h3 class="lyric-artist">Artista de prueba</h3>
    <pre id="lyric-body-text">
Primera línea de prueba<br>
Segunda línea &amp; tercera
    </pre>
</html>
"""


class TestLyricsComProvider(unittest.TestCase):

    def test_extracts_lyrics_and_validates_metadata(self):
        result = parse_lyrics_page(
            SAMPLE_HTML,
            "Artista de prueba",
            "Canción de prueba",
        )

        self.assertEqual(result.status, "FOUND")
        self.assertEqual(result.artist, "Artista de prueba")
        self.assertEqual(result.title, "Canción de prueba")
        self.assertEqual(result.source, "lyrics.com")
        self.assertIn("Primera línea de prueba", result.lyrics)
        self.assertIn("Segunda línea & tercera", result.lyrics)

    def test_rejects_wrong_artist(self):
        result = parse_lyrics_page(
            SAMPLE_HTML,
            "Otro artista",
            "Canción de prueba",
        )

        self.assertEqual(result.status, "NOT_FOUND")
        self.assertIn("artista", result.message.lower())

    def test_rejects_wrong_title(self):
        result = parse_lyrics_page(
            SAMPLE_HTML,
            "Artista de prueba",
            "Otro título",
        )

        self.assertEqual(result.status, "NOT_FOUND")
        self.assertIn("título", result.message.lower())

    def test_rejects_page_without_lyrics_block(self):
        html_without_lyrics = """
        <h1 id="lyric-title-text">Canción de prueba</h1>
        <h3 class="lyric-artist">Artista de prueba</h3>
        """

        result = parse_lyrics_page(
            html_without_lyrics,
            "Artista de prueba",
            "Canción de prueba",
        )

        self.assertEqual(result.status, "NOT_FOUND")
        self.assertIn("lyric-body-text", result.message)


if __name__ == "__main__":
    unittest.main()
