from pathlib import Path
from urllib.parse import quote
import re
import shutil
import unicodedata
from html import unescape


import requests
from mutagen.id3 import ID3, USLT


LYRICS_API = "https://api.lyrics.ovh/v1"


from models import LyricsResult
from metadata import get_metadata, read_existing_lyrics
from writer import create_backup, write_lyrics
from providers.lyricsweb import search_lyrics_lyricsweb


def generate_title_variants(title):
    """
    Genera variantes del título para aumentar
    las posibilidades de encontrar la canción.
    """

    variants = []

    # 1. Original
    variants.append(("original", title))

    # 2. Sin apóstrofes
    no_apostrophe = re.sub(r"['’‘`´]", "", title)

    if no_apostrophe != title:
        variants.append(("sin_apostrofe", no_apostrophe))

    # 3. Guiones convertidos en espacios
    dash_space = re.sub(r"[-–—]", " ", title)
    dash_space = re.sub(r"\s+", " ", dash_space).strip()

    if dash_space != title:
        variants.append(("guion_a_espacio", dash_space))

    # 4. Sin paréntesis
    no_parentheses = re.sub(r"\s*\([^)]*\)", "", title)
    no_parentheses = re.sub(r"\s+", " ", no_parentheses).strip()

    if no_parentheses != title:
        variants.append(("sin_parentesis", no_parentheses))

    # 5. Sin paréntesis + sin apóstrofes
    no_parentheses_apostrophe = re.sub(
        r"['’‘`´]",
        "",
        no_parentheses,
    )

    if no_parentheses_apostrophe != title:
        variants.append(
            (
                "sin_parentesis_sin_apostrofe",
                no_parentheses_apostrophe,
            )
        )

    # 6. Normalización Unicode
    normalized = unicodedata.normalize("NFKD", title)
    normalized = "".join(
        c for c in normalized
        if not unicodedata.combining(c)
    )

    if normalized != title:
        variants.append(("unicode_normalizado", normalized))

    # 7. Unicode normalizado + sin apóstrofes
    normalized_apostrophe = re.sub(
        r"['’‘`´]",
        "",
        normalized,
    )

    if normalized_apostrophe != title:
        variants.append(
            (
                "unicode_normalizado_sin_apostrofe",
                normalized_apostrophe,
            )
        )

    # Eliminar duplicados conservando el orden
    result = []
    seen = set()

    for name, value in variants:

        key = value.strip()

        if key not in seen:
            seen.add(key)
            result.append((name, key))

    return result

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
    # ALIASES ESPECIALES
    # --------------------------------------------------

    artist_aliases = [
        artist,
    ]

    special_artist_aliases = {
        (
            "steve perry",
            "don't fight it",
        ): [
            "Kenny Loggins & Steve Perry",
        ],
    }

    alias_key = (
        artist.strip().lower(),
        title.strip().lower(),
    )

    if alias_key in special_artist_aliases:
        artist_aliases.extend(
            special_artist_aliases[alias_key]
        )

    last_message = None

    # --------------------------------------------------
    # Buscar en lyrics.ovh
    # --------------------------------------------------

    for search_artist in artist_aliases:

        variants = generate_title_variants(title)

        for variant_name, query_title in variants:

            url = (
                f"{LYRICS_API}/"
                f"{quote(search_artist)}/"
                f"{quote(query_title)}"
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
                last_message = (
                    f"HTTP {response.status_code}"
                )
                continue

            try:
                data = response.json()

            except ValueError:

                last_message = (
                    "Respuesta JSON inválida."
                )
                continue

            lyrics = data.get("lyrics")

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
