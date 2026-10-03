#!/usr/bin/env python3

import unittest
from unittest.mock import patch

from lyrics_engine import search_lyrics


class TestArtistAliases(unittest.TestCase):

    @patch("lyrics_engine.engine.search_lyrics_lyricsweb")
    @patch("lyrics_engine.engine.search_lyrics_ovh")
    def test_dont_fight_it_uses_artist_alias(
        self,
        mock_ovh,
        mock_lyricsweb,
    ):
        """
        Verifica que:

        Steve Perry / Don't Fight It

        también pruebe con:

        Kenny Loggins & Steve Perry
        """

        class FakeResult:
            def __init__(
                self,
                status,
                lyrics=None,
                message=None,
            ):
                self.status = status
                self.lyrics = lyrics
                self.message = message

        calls = []

        def fake_ovh(artist, title):
            calls.append((artist, title))

            if artist == "Kenny Loggins & Steve Perry":
                return FakeResult(
                    status="FOUND",
                    lyrics="Letra de prueba",
                )

            return FakeResult(
                status="NOT_FOUND",
                message="No encontrada",
            )

        mock_ovh.side_effect = fake_ovh

        result = search_lyrics(
            "Steve Perry",
            "Don't Fight It",
        )

        self.assertEqual(
            result.status,
            "FOUND",
        )

        self.assertEqual(
            result.artist,
            "Steve Perry",
        )

        self.assertEqual(
            result.title,
            "Don't Fight It",
        )

        self.assertEqual(
            result.lyrics,
            "Letra de prueba",
        )

        self.assertTrue(
            any(
                artist == "Kenny Loggins & Steve Perry"
                for artist, title in calls
            )
        )

        mock_lyricsweb.assert_not_called()


if __name__ == "__main__":
    unittest.main()
