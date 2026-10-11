import re
from html import unescape

import requests

from ..models import LyricsResult


def _slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _title_variants(title):
    """Genera variantes conservadoras del título original."""
    variantes = [title.strip()]

    # Eliminar etiquetas editoriales entre paréntesis,
    # por ejemplo: (2008 Remaster), (Live), (Remastered).
    sin_etiquetas = re.sub(
        r"\s*\((?=[^)]*(?:remaster|remastered|live|deluxe|edit|version|edition|bonus|mono|stereo|202\d|200\d))[^)]*\)",
        "",
        title,
        flags=re.IGNORECASE,
    ).strip()

    if sin_etiquetas and sin_etiquetas not in variantes:
        variantes.append(sin_etiquetas)

    # Probar también títulos sin apóstrofos cuando el sitio
    # utiliza una URL distinta para esa variante.
    for variante in list(variantes):
        sin_apostrofos = variante.replace("'", "").replace("’", "")
        if sin_apostrofos and sin_apostrofos not in variantes:
            variantes.append(sin_apostrofos)

    return variantes


def search_lyrics_lyricsweb(artist, title):
    """
    Busca y extrae letras desde LyricsWeb.

    No modifica ningún archivo MP3.
    """

    special_urls = {
        (
            "kenny loggins & steve perry",
            "don't fight it",
        ): (
            "https://lyricsweb.com/song/"
            "kenny-loggins/"
            "kenny-loggins-dont-fight-it"
        ),
    }

    key = (artist.strip().lower(), title.strip().lower())

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/130.0 Safari/537.36"
        )
    }

    if key in special_urls:
        urls = [special_urls[key]]
    else:
        artist_slug = _slug(artist)
        urls = [
            (
                f"https://lyricsweb.com/song/{artist_slug}/"
                f"{artist_slug}-{_slug(variant)}"
            )
            for variant in _title_variants(title)
        ]

    # No consultar dos veces una misma URL.
    urls = list(dict.fromkeys(urls))
    ultimo_mensaje = "No se encontró una página válida"

    for url in urls:
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=20,
            )
        except requests.RequestException as e:
            ultimo_mensaje = f"Error de conexión: {e}"
            continue

        if response.status_code != 200:
            ultimo_mensaje = f"HTTP {response.status_code}"
            continue

        pattern = re.compile(
            r'<div\s+id="lyrics-panel"[^>]*>(.*?)</div>',
            re.IGNORECASE | re.DOTALL,
        )
        match = pattern.search(response.text)

        if not match:
            ultimo_mensaje = "No se encontró lyrics-panel"
            continue

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

        lines = []
        for line in block.splitlines():
            line = line.strip()
            if line:
                lines.append(line)
            elif lines and lines[-1] != "":
                lines.append("")

        lyrics = "\n".join(lines).strip()

        if not lyrics:
            ultimo_mensaje = "lyrics-panel estaba vacío"
            continue

        return LyricsResult(
            status="FOUND",
            artist=artist,
            title=title,
            lyrics=lyrics,
            source="lyricsweb",
            message="Encontrado mediante LyricsWeb",
        )

    return LyricsResult(
        status="NOT_FOUND",
        artist=artist,
        title=title,
        source="lyricsweb",
        message=ultimo_mensaje,
    )
