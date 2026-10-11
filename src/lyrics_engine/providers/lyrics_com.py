"""Provider independiente para páginas de letras de Lyrics.com."""

import re
from html import unescape

import requests

from ..models import LyricsResult


SOURCE = "lyrics.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/130.0 Safari/537.36"
    )
}


def _normalise(value):
    """Normaliza puntuación, espacios y mayúsculas para comparar metadatos."""
    value = unescape(value).casefold()
    value = re.sub(r"[^\w\s]", "", value)
    return " ".join(value.split())


def _extract_element(pattern, html):
    """Extrae el contenido del primer elemento que coincida."""
    match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)

    if not match:
        return None

    value = re.sub(r"<[^>]+>", "", match.group(1))
    return unescape(value).strip()


def parse_lyrics_page(html, artist, title):
    """
    Analiza el HTML de una página de Lyrics.com.

    Devuelve LyricsResult sin realizar peticiones de red.
    """
    page_title = _extract_element(
        r'<[^>]+id=["\']lyric-title-text["\'][^>]*>(.*?)</[^>]+>',
        html,
    )
    page_artist = _extract_element(
        r'<[^>]+class=["\'][^"\']*\blyric-artist\b[^"\']*["\'][^>]*>'
        r'(.*?)</[^>]+>',
        html,
    )

    if not page_title or not page_artist:
        return LyricsResult(
            status="NOT_FOUND",
            artist=artist,
            title=title,
            source=SOURCE,
            message="No se pudieron validar artista y título en la página",
        )

    if _normalise(page_artist) != _normalise(artist):
        return LyricsResult(
            status="NOT_FOUND",
            artist=artist,
            title=title,
            source=SOURCE,
            message="El artista de la página no coincide",
        )

    if _normalise(page_title) != _normalise(title):
        return LyricsResult(
            status="NOT_FOUND",
            artist=artist,
            title=title,
            source=SOURCE,
            message="El título de la página no coincide",
        )

    match = re.search(
        r'<pre\b(?=[^>]*\bid=["\']lyric-body-text["\'])[^>]*>'
        r'(.*?)</pre\s*>',
        html,
        re.IGNORECASE | re.DOTALL,
    )

    if not match:
        return LyricsResult(
            status="NOT_FOUND",
            artist=artist,
            title=title,
            source=SOURCE,
            message="No se encontró pre#lyric-body-text",
        )

    block = match.group(1)

    block = re.sub(
        r"<br\s*/?>",
        "\n",
        block,
        flags=re.IGNORECASE,
    )
    block = re.sub(
        r"</p\s*>",
        "\n",
        block,
        flags=re.IGNORECASE,
    )
    block = re.sub(r"<[^>]+>", "", block)
    block = unescape(block)

    lyrics = "\n".join(
        line.rstrip()
        for line in block.splitlines()
    ).strip()

    if not lyrics:
        return LyricsResult(
            status="NOT_FOUND",
            artist=artist,
            title=title,
            source=SOURCE,
            message="El bloque de letras está vacío",
        )

    return LyricsResult(
        status="FOUND",
        artist=page_artist,
        title=page_title,
        lyrics=lyrics,
        source=SOURCE,
        message="Encontrado mediante Lyrics.com",
    )


def search_lyrics_lyrics_com(artist, title, url):
    """
    Descarga y analiza una URL concreta de Lyrics.com.

    La URL debe haber sido identificada previamente.
    No realiza búsquedas genéricas ni modifica archivos MP3.
    """
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20,
        )
        response.raise_for_status()

    except requests.RequestException as exc:
        return LyricsResult(
            status="ERROR",
            artist=artist,
            title=title,
            source=SOURCE,
            message=f"Error de conexión: {type(exc).__name__}",
        )

    return parse_lyrics_page(
        response.text,
        artist,
        title,
    )


def search_lyrics_com(artist, title):
    """
    Busca una canción en Lyrics.com y valida los enlaces candidatos.

    No modifica archivos de música.
    """
    from urllib.parse import quote, unquote_plus, urljoin, urlparse

    search_url = (
        "https://www.lyrics.com/lyrics/"
        f"{quote(artist, safe='')}/{quote(title, safe='')}"
    )

    try:
        response = requests.get(
            search_url,
            headers=HEADERS,
            timeout=20,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        return LyricsResult(
            status="ERROR",
            artist=artist,
            title=title,
            source=SOURCE,
            message=f"Error al buscar: {type(exc).__name__}",
        )

    links = re.findall(
        r"""<a\b[^>]*href=["']([^"']*/(?:lyric|lyric-lf)/[^"']*)["']""",
        response.text,
        re.IGNORECASE,
    )

    candidates = []
    seen = set()

    for link in links:
        link = unescape(link.strip())
        candidate_url = urljoin("https://www.lyrics.com/", link)
        parsed = urlparse(candidate_url)

        if parsed.netloc.lower() not in {"lyrics.com", "www.lyrics.com"}:
            continue

        parts = parsed.path.split("/")
        if len(parts) < 5 or parts[1] not in {"lyric", "lyric-lf"}:
            continue

        page_artist = unquote_plus(parts[3])
        page_title = unquote_plus(parts[4])

        if _normalise(page_artist) != _normalise(artist):
            continue

        if _normalise(page_title) != _normalise(title):
            continue

        if candidate_url not in seen:
            seen.add(candidate_url)
            candidates.append(candidate_url)

    if not candidates:
        return LyricsResult(
            status="NOT_FOUND",
            artist=artist,
            title=title,
            source=SOURCE,
            message="No se encontraron enlaces con artista y título coincidentes",
        )

    last_error = None

    for candidate_url in candidates:
        result = search_lyrics_lyrics_com(
            artist,
            title,
            candidate_url,
        )

        if result.status == "FOUND":
            return result

        if result.status == "ERROR":
            last_error = result

    if last_error is not None:
        return last_error

    return LyricsResult(
        status="NOT_FOUND",
        artist=artist,
        title=title,
        source=SOURCE,
        message="Se encontraron candidatos, pero ninguno pasó la validación",
    )
