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


def get_metadata(mp3_path):
    """
    Lee artista y título desde los tags ID3.
    No modifica el archivo.
    """

    try:
        audio = ID3(mp3_path)

        artist = audio.get("TPE1")
        title = audio.get("TIT2")

        artist = str(artist) if artist else None
        title = str(title) if title else None

        if not artist or not title:
            return LyricsResult(
                status="ERROR",
                message="No se pudo obtener artista/título desde los tags.",
            )

        return LyricsResult(
            status="OK",
            artist=artist,
            title=title,
        )

    except Exception as e:
        return LyricsResult(
            status="ERROR",
            message=f"Error leyendo metadata: {e}",
        )


def read_existing_lyrics(mp3_path):
    """
    Devuelve los frames USLT existentes.
    No modifica el archivo.
    """

    try:
        audio = ID3(mp3_path)

        return audio.getall("USLT")

    except Exception:
        return []


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


def create_backup(mp3_path):
    """
    Crea una copia .bak del MP3.
    Nunca sobrescribe un backup existente.
    """

    mp3_path = Path(mp3_path)
    backup_path = mp3_path.with_suffix(
        mp3_path.suffix + ".bak"
    )

    if backup_path.exists():
        return backup_path

    shutil.copy2(
        mp3_path,
        backup_path,
    )

    return backup_path


def write_lyrics(
    mp3_path,
    lyrics,
    language="eng",
    description="Lyrics",
    overwrite=False,
):
    """
    Escribe lyrics en un frame ID3 USLT.

    Antes de modificar:
    - comprueba si ya existen lyrics
    - crea backup .bak
    """

    try:
        audio = ID3(mp3_path)

        existing = audio.getall("USLT")

        if existing and not overwrite:

            return LyricsResult(
                status="ALREADY_EXISTS",
                message=(
                    "El archivo ya contiene lyrics."
                ),
            )

        backup_path = create_backup(mp3_path)

        if overwrite:

            audio.delall("USLT")

        audio.add(
            USLT(
                encoding=3,
                lang=language,
                desc=description,
                text=lyrics,
            )
        )

        audio.save(
            mp3_path,
            v2_version=3,
        )

        return LyricsResult(
            status="WRITTEN",
            message=(
                f"Lyrics guardadas. "
                f"Backup: {backup_path}"
            ),
        )

    except Exception as e:

        return LyricsResult(
            status="ERROR",
            message=f"Error escribiendo lyrics: {e}",
        )
