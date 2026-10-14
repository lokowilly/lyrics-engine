"""Proveedor independiente para la API de LRCLIB."""

import re
import unicodedata

import requests

from ..models import LyricsResult


SOURCE = "LRCLIB"
API_URL = "https://lrclib.net/api/search"
HEADERS = {
    "User-Agent": (
        "LyricsEngine/0.1 "
        "(https://github.com/lokowilly/lyrics-engine)"
    )
}
TIMEOUT = 15


def _normalise(value):
    """Normaliza mayúsculas, acentos, puntuación y espacios."""
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(
        char for char in value
        if not unicodedata.combining(char)
    )
    value = value.casefold()
    value = re.sub(r"[^\w\s]", "", value)
    return " ".join(value.split())


def _plain_text(item):
    """Devuelve texto plano, convirtiendo letras sincronizadas si hace falta."""
    lyrics = item.get("plainLyrics")

    if isinstance(lyrics, str) and lyrics.strip():
        return lyrics.strip()

    synced = item.get("syncedLyrics")
    if not isinstance(synced, str) or not synced.strip():
        return None

    # Elimina marcas como [00:22.19] sin alterar el resto de cada línea.
    lines = [
        re.sub(r"^\s*\[\d{1,2}:\d{2}(?:[.:]\d{1,3})?\]\s?", "", line)
        for line in synced.splitlines()
    ]
    text = "\n".join(lines).strip()
    return text or None


def search_lyrics_lrclib(artist, title):
    """
    Busca candidatos en LRCLIB y acepta solo coincidencias exactas
    tras normalizar artista y título.

    No modifica archivos ni registra el contenido de las letras.
    """
    try:
        response = requests.get(
            API_URL,
            params={
                "artist_name": artist,
                "track_name": title,
            },
            headers=HEADERS,
            timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        return LyricsResult(
            status="ERROR",
            artist=artist,
            title=title,
            source=SOURCE,
            message=f"Error de conexión: {type(exc).__name__}",
        )

    if response.status_code == 429:
        retry_after = response.headers.get("Retry-After")
        return LyricsResult(
            status="ERROR",
            artist=artist,
            title=title,
            source=SOURCE,
            message=(
                "LRCLIB limitó las consultas"
                + (f"; Retry-After: {retry_after}" if retry_after else "")
            ),
        )

    if response.status_code >= 500:
        return LyricsResult(
            status="ERROR",
            artist=artist,
            title=title,
            source=SOURCE,
            message=f"LRCLIB respondió HTTP {response.status_code}",
        )

    if response.status_code == 404:
        return LyricsResult(
            status="NOT_FOUND",
            artist=artist,
            title=title,
            source=SOURCE,
            message="LRCLIB no encontró coincidencias",
        )

    if response.status_code != 200:
        return LyricsResult(
            status="ERROR",
            artist=artist,
            title=title,
            source=SOURCE,
            message=f"Respuesta inesperada de LRCLIB: HTTP {response.status_code}",
        )

    try:
        candidates = response.json()
    except ValueError:
        return LyricsResult(
            status="ERROR",
            artist=artist,
            title=title,
            source=SOURCE,
            message="LRCLIB devolvió una respuesta JSON inválida",
        )

    if not isinstance(candidates, list):
        return LyricsResult(
            status="ERROR",
            artist=artist,
            title=title,
            source=SOURCE,
            message="Formato de respuesta inesperado de LRCLIB",
        )

    for item in candidates:
        if not isinstance(item, dict):
            continue

        if _normalise(item.get("artistName")) != _normalise(artist):
            continue

        if _normalise(item.get("trackName")) != _normalise(title):
            continue

        lyrics = _plain_text(item)
        if not lyrics:
            continue

        return LyricsResult(
            status="FOUND",
            artist=artist,
            title=title,
            lyrics=lyrics,
            source=SOURCE,
            message="Encontrado mediante LRCLIB",
            query_title=title,
        )

    return LyricsResult(
        status="NOT_FOUND",
        artist=artist,
        title=title,
        source=SOURCE,
        message="LRCLIB no devolvió una coincidencia exacta con letras",
    )
