import re
from html import unescape

import requests

from ..models import LyricsResult


def search_lyrics_lyricsweb(artist, title):
    """
    Busca y extrae letras desde LyricsWeb.

    Este proveedor se utiliza como fallback cuando lyrics.ovh
    no encuentra la canción.

    No modifica ningún archivo MP3.
    """

    # URLs conocidas que requieren un slug especial.
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

    key = (
        artist.strip().lower(),
        title.strip().lower(),
    )

    if key in special_urls:
        url = special_urls[key]

    else:
        artist_slug = re.sub(
            r"[^a-z0-9]+",
            "-",
            artist.lower(),
        ).strip("-")

        title_slug = re.sub(
            r"[^a-z0-9]+",
            "-",
            title.lower(),
        ).strip("-")

        url = (
            f"https://lyricsweb.com/song/"
            f"{artist_slug}/"
            f"{artist_slug}-{title_slug}"
        )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/130.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=20,
        )

    except requests.RequestException as e:

        return LyricsResult(
            status="NOT_FOUND",
            artist=artist,
            title=title,
            source="lyricsweb",
            message=f"Error de conexión: {e}",
        )

    if response.status_code != 200:

        return LyricsResult(
            status="NOT_FOUND",
            artist=artist,
            title=title,
            source="lyricsweb",
            message=f"HTTP {response.status_code}",
        )

    html = response.text

    # --------------------------------------------------
    # Buscar el panel real de letras
    # --------------------------------------------------

    pattern = re.compile(
        r'<div\s+id="lyrics-panel"[^>]*>'
        r'(.*?)'
        r'</div>',
        re.IGNORECASE | re.DOTALL,
    )

    match = pattern.search(html)

    if not match:

        return LyricsResult(
            status="NOT_FOUND",
            artist=artist,
            title=title,
            source="lyricsweb",
            message="No se encontró lyrics-panel",
        )

    block = match.group(1)

    # HTML -> saltos de línea
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

    # Eliminar etiquetas HTML restantes
    block = re.sub(
        r"<[^>]+>",
        "",
        block,
    )

    # Entidades HTML:
    # &#x27; -> '
    # &amp;   -> &
    block = unescape(block)

    # --------------------------------------------------
    # Limpiar líneas
    # --------------------------------------------------

    lines = []

    for line in block.splitlines():

        line = line.strip()

        if line:
            lines.append(line)

        elif lines and lines[-1] != "":
            lines.append("")

    lyrics = "\n".join(lines).strip()

    if not lyrics:

        return LyricsResult(
            status="NOT_FOUND",
            artist=artist,
            title=title,
            source="lyricsweb",
            message="lyrics-panel estaba vacío",
        )

    return LyricsResult(
        status="FOUND",
        artist=artist,
        title=title,
        lyrics=lyrics,
        source="lyricsweb",
        message="Encontrado mediante LyricsWeb",
    )
