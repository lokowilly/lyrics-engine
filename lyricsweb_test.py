#!/usr/bin/env python3

import re
import requests
from html import unescape


TESTS = [
    (
        "Steve Perry",
        "Against the Wall",
        "https://lyricsweb.com/song/steve-perry/steve-perry-against-the-wall",
    ),
    (
        "Steve Perry",
        "Once in a Lifetime, Girl",
        "https://lyricsweb.com/song/steve-perry/steve-perry-once-in-a-lifetime-girl",
    ),
    (
        "Steve Perry",
        "I Stand Alone",
        "https://lyricsweb.com/song/steve-perry/steve-perry-i-stand-alone",
    ),
    (
        "Steve Perry",
        "If You Need Me, Call Me",
        "https://lyricsweb.com/song/steve-perry/steve-perry-if-you-need-me-call-me",
    ),
    (
        "Kenny Loggins & Steve Perry",
        "Don't Fight It",
        "https://lyricsweb.com/song/kenny-loggins/kenny-loggins-dont-fight-it",
    ),
]


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/130.0 Safari/537.36"
    )
}


def extract_lyrics(html):
    """
    Extrae la letra desde:

        <div id="lyrics-panel">
            <p ...>LETRA</p>
        </div>

    No modifica archivos de música.
    """

    pattern = re.compile(
        r'<div\s+id="lyrics-panel"[^>]*>'
        r'(.*?)'
        r'</div>',
        re.IGNORECASE | re.DOTALL,
    )

    match = pattern.search(html)

    if not match:
        return None

    block = match.group(1)

    # El bloque contiene normalmente uno o más <p>.
    # Convertimos saltos HTML en saltos reales.
    block = re.sub(
        r'<br\s*/?>',
        '\n',
        block,
        flags=re.IGNORECASE,
    )

    block = re.sub(
        r'</p\s*>',
        '\n',
        block,
        flags=re.IGNORECASE,
    )

    # Eliminar cualquier otra etiqueta HTML.
    block = re.sub(
        r'<[^>]+>',
        '',
        block,
    )

    # Convertir entidades HTML:
    # &#x27; -> '
    # &amp;   -> &
    # etc.
    block = unescape(block)

    # Normalizar saltos de línea.
    lines = []

    for line in block.splitlines():

        line = line.strip()

        if line:
            lines.append(line)
        elif lines and lines[-1] != "":
            lines.append("")

    lyrics = "\n".join(lines)

    # Limpiar espacios/saltos sobrantes.
    lyrics = lyrics.strip()

    return lyrics


def test_song(artist, title, url):

    print("-" * 70)
    print(f"Artista : {artist}")
    print(f"Título  : {title}")
    print(f"URL     : {url}")

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20,
        )

    except requests.RequestException as e:

        print(f"ERROR      : {e}")
        return None

    print(f"HTTP       : {response.status_code}")

    if response.status_code != 200:

        print("Caracteres : 0")
        print("RESULTADO  : NOT_FOUND")

        return None

    lyrics = extract_lyrics(response.text)

    if not lyrics:

        print("Caracteres : 0")
        print("RESULTADO  : LYRICS_NOT_FOUND")

        return None

    print(f"Caracteres : {len(lyrics)}")

    # --------------------------------------------------
    # Vista previa
    # --------------------------------------------------

    preview = lyrics.replace("\n", " ")

    if len(preview) > 120:
        preview = preview[:120] + "..."

    print(f"Muestra    : {preview}")
    print("RESULTADO  : LYRICS_OK")

    return lyrics


def main():

    print("=" * 70)
    print("LABORATORIO LYRICSWEB")
    print("Extracción de letras — SIN modificar MP3")
    print("=" * 70)

    results = []

    for artist, title, url in TESTS:

        lyrics = test_song(
            artist,
            title,
            url,
        )

        results.append(
            (
                artist,
                title,
                lyrics,
            )
        )

    print()
    print("=" * 70)
    print("RESUMEN")
    print("=" * 70)

    found = 0
    not_found = 0

    for artist, title, lyrics in results:

        if lyrics:

            found += 1

            print(
                f"✅ {title:<45} "
                f"{len(lyrics):>6} caracteres"
            )

        else:

            not_found += 1

            print(
                f"❌ {title:<45} "
                f"NO ENCONTRADA"
            )

    print("-" * 70)
    print(f"Encontradas   : {found}")
    print(f"No encontradas: {not_found}")
    print("=" * 70)


if __name__ == "__main__":
    main()
