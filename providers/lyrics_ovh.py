from urllib.parse import quote

import requests

from models import LyricsResult


LYRICS_API = "https://api.lyrics.ovh/v1"


def search_lyrics_ovh(artist, title):
    """
    Busca lyrics directamente en lyrics.ovh.

    No genera variantes ni aliases.
    Recibe un artista y título ya preparados.
    No modifica archivos MP3.
    """

    url = (
        f"{LYRICS_API}/"
        f"{quote(artist)}/"
        f"{quote(title)}"
    )

    try:
        response = requests.get(
            url,
            timeout=15,
        )

    except requests.RequestException as e:

        return LyricsResult(
            status="ERROR",
            artist=artist,
            title=title,
            source="lyrics.ovh",
            message=f"Error de conexión: {e}",
        )

    if response.status_code != 200:

        return LyricsResult(
            status="NOT_FOUND",
            artist=artist,
            title=title,
            source="lyrics.ovh",
            message=f"HTTP {response.status_code}",
        )

    try:
        data = response.json()

    except ValueError as e:

        return LyricsResult(
            status="NOT_FOUND",
            artist=artist,
            title=title,
            source="lyrics.ovh",
            message=f"JSON inválido: {e}",
        )

    lyrics = data.get("lyrics")

    if lyrics:

        return LyricsResult(
            status="FOUND",
            artist=artist,
            title=title,
            lyrics=lyrics,
            source="lyrics.ovh",
        )

    return LyricsResult(
        status="NOT_FOUND",
        artist=artist,
        title=title,
        source="lyrics.ovh",
        message="La respuesta no contiene lyrics.",
    )
