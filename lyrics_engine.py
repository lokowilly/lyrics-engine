from models import LyricsResult
from metadata import get_metadata, read_existing_lyrics
from writer import create_backup, write_lyrics
from providers.lyricsweb import search_lyrics_lyricsweb
from providers.lyrics_ovh import search_lyrics_ovh
from aliases import get_artist_aliases
from title_variants import generate_title_variants

def search_lyrics(artist, title):
    """
    Busca lyrics usando lyrics.ovh y varias variantes
    del título.

    Si no encuentra la canción, prueba LyricsWeb.
    También permite aliases de artista para canciones
    donde el tag del MP3 no coincide con el artista
    utilizado por las fuentes de letras.
    """

    # --------------------------------------------------
    # ALIASES DE ARTISTA
    # --------------------------------------------------

    artist_aliases = get_artist_aliases(
        artist,
        title,
    )

    last_message = None

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

            if search_artist != artist:
                result.message = (
                    f"Encontrado mediante LyricsWeb"
                    f" | artista alternativo: "
                    f"{search_artist}"
                )

            return result

    return LyricsResult(
        status="NOT_FOUND",
        artist=artist,
        title=title,
        source="lyrics.ovh",
        message=last_message or "Lyrics no encontradas.",
    )
