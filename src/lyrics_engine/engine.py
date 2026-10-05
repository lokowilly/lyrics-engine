import time

from .models import LyricsResult
from .providers.lyricsweb import search_lyrics_lyricsweb
from .providers.lyrics_ovh import search_lyrics_ovh
from .aliases import get_artist_aliases
from .title_variants import generate_title_variants


def _search_lyrics_once(artist, title, attempt=1):
    """
    Realiza una búsqueda completa de lyrics.

    Incluye:
    - aliases de artista
    - variantes de título
    - lyrics.ovh
    - fallback a LyricsWeb

    Esta función representa UN intento completo.
    """

    # --------------------------------------------------
    # ALIASES DE ARTISTA
    # --------------------------------------------------

    artist_aliases = get_artist_aliases(
        artist,
        title,
    )

    last_message = None
    lyricsweb_message = None

    # --------------------------------------------------
    # Buscar en lyrics.ovh
    # --------------------------------------------------

    for search_artist in artist_aliases:

        variants = generate_title_variants(title)

        for variant_name, query_title in variants:

            provider_result = search_lyrics_ovh(
                search_artist,
                query_title,
            )

            if provider_result.status == "ERROR":

                return LyricsResult(
                    status="ERROR",
                    artist=artist,
                    title=title,
                    source="lyrics.ovh",
                    message=provider_result.message,
                    attempt=attempt,
                )

            if provider_result.status != "FOUND":

                last_message = provider_result.message
                continue

            lyrics = provider_result.lyrics

            if lyrics and lyrics.strip():

                message = (
                    f"Encontrado mediante variante: "
                    f"{variant_name}"
                )

                if search_artist != artist:
                    message += (
                        f" | artista alternativo: "
                        f"{search_artist}"
                    )

                return LyricsResult(
                    status="FOUND",
                    artist=artist,
                    title=title,
                    lyrics=lyrics.strip(),
                    source="lyrics.ovh",
                    variant=variant_name,
                    query_title=query_title,
                    message=message,
                    attempt=attempt,
                )

            last_message = (
                "La respuesta no contiene lyrics."
            )

    # --------------------------------------------------
    # FALLBACK: LyricsWeb
    # --------------------------------------------------

    for search_artist in artist_aliases:

        result = search_lyrics_lyricsweb(
            search_artist,
            title,
        )

        if result.status == "FOUND":

            # Conservamos como artista el artista
            # original del MP3.
            result.artist = artist
            result.title = title
            result.attempt = attempt
            if search_artist != artist:
                result.message = (
                    f"Encontrado mediante LyricsWeb"
                    f" | artista alternativo: "
                    f"{search_artist}"
                )

            return result

        # Guardamos el resultado de LyricsWeb para
        # poder informar correctamente el diagnóstico.
        lyricsweb_message = result.message

    diagnostic_parts = []

    if last_message:
        diagnostic_parts.append(
            f"lyrics.ovh: {last_message}"
        )

    if lyricsweb_message:
        diagnostic_parts.append(
            f"LyricsWeb: {lyricsweb_message}"
        )

    return LyricsResult(
        status="NOT_FOUND",
        artist=artist,
        title=title,
        source="lyrics.ovh",
        message=(
            " | ".join(diagnostic_parts)
            if diagnostic_parts
            else "Lyrics no encontradas."
        ),
        attempt=attempt,
    )


def search_lyrics(artist, title):
    """
    Busca lyrics realizando hasta dos búsquedas completas.

    Si el primer intento termina en FOUND, retorna
    inmediatamente.

    Si termina en NOT_FOUND o ERROR, realiza un
    segundo intento completo.
    """

    # --------------------------------------------------
    # PRIMER INTENTO
    # --------------------------------------------------

    result = _search_lyrics_once(
        artist,
        title,
        attempt=1,
    )

    if result.status == "FOUND":
        return result

    # --------------------------------------------------
    # BACKOFF ANTES DEL SEGUNDO INTENTO
    # --------------------------------------------------

    time.sleep(1)

    # --------------------------------------------------
    # SEGUNDO INTENTO
    # --------------------------------------------------

    return _search_lyrics_once(
        artist,
        title,
        attempt=2,
    )
