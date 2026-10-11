import time

from .models import LyricsResult
from .providers.lyricsweb import search_lyrics_lyricsweb
from .providers.lyrics_ovh import search_lyrics_ovh
from .providers.lyrics_com import search_lyrics_com
from .aliases import get_artist_aliases
from .title_variants import generate_title_variants


def _search_lyrics_once(artist, title, attempt=1):
    """
    Realiza una búsqueda completa de lyrics.

    Orden de proveedores:
    1. lyrics.ovh con aliases y variantes del título.
    2. LyricsWeb con aliases de artista.
    3. Lyrics.com como último recurso.
    """

    artist_aliases = get_artist_aliases(artist, title)
    last_messages = {}
    last_statuses = {}

    # --------------------------------------------------
    # PROVEEDOR 1: lyrics.ovh
    # --------------------------------------------------

    for search_artist in artist_aliases:
        variants = generate_title_variants(title)

        for variant_name, query_title in variants:
            result = search_lyrics_ovh(search_artist, query_title)

            if result.status == "FOUND" and result.lyrics:
                message = f"Encontrado mediante variante: {variant_name}"

                if search_artist != artist:
                    message += f" | artista alternativo: {search_artist}"

                return LyricsResult(
                    status="FOUND",
                    artist=artist,
                    title=title,
                    lyrics=result.lyrics.strip(),
                    source="lyrics.ovh",
                    variant=variant_name,
                    query_title=query_title,
                    message=message,
                    attempt=attempt,
                )

            last_messages["lyrics.ovh"] = result.message
            last_statuses["lyrics.ovh"] = result.status

    # --------------------------------------------------
    # PROVEEDOR 2: LyricsWeb
    # --------------------------------------------------

    for search_artist in artist_aliases:
        result = search_lyrics_lyricsweb(search_artist, title)

        if result.status == "FOUND" and result.lyrics:
            result.artist = artist
            result.title = title
            result.attempt = attempt

            if search_artist != artist:
                result.message = (
                    "Encontrado mediante LyricsWeb"
                    f" | artista alternativo: {search_artist}"
                )

            return result

        last_messages["LyricsWeb"] = result.message
        last_statuses["LyricsWeb"] = result.status

    # --------------------------------------------------
    # PROVEEDOR 3: Lyrics.com
    # --------------------------------------------------

    result = search_lyrics_com(artist, title)

    if result.status == "FOUND" and result.lyrics:
        result.artist = artist
        result.title = title
        result.attempt = attempt
        return result

    last_messages["Lyrics.com"] = result.message
    last_statuses["Lyrics.com"] = result.status

    # --------------------------------------------------
    # DIAGNÓSTICO FINAL
    # --------------------------------------------------

    diagnostic_parts = [
        f"{provider}: {message}"
        for provider, message in last_messages.items()
        if message
    ]

    all_providers_failed = (
        len(last_statuses) == 3
        and all(status == "ERROR" for status in last_statuses.values())
    )

    return LyricsResult(
        status="ERROR" if all_providers_failed else "NOT_FOUND",
        artist=artist,
        title=title,
        source=None,
        message=(
            " | ".join(diagnostic_parts)
            if diagnostic_parts
            else "Lyrics no encontradas."
        ),
        attempt=attempt,
    )


def search_lyrics(artist, title):
    """
    Busca lyrics realizando hasta dos intentos completos.
    """

    result = _search_lyrics_once(artist, title, attempt=1)

    if result.status == "FOUND":
        return result

    time.sleep(1)

    return _search_lyrics_once(artist, title, attempt=2)
