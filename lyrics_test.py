#!/usr/bin/env python3

import sys
import requests
from urllib.parse import quote


def search_lyrics(artist, title):
    url = (
        f"https://api.lyrics.ovh/v1/"
        f"{quote(artist)}/"
        f"{quote(title)}"
    )

    print(f"URL: {url}")
    print()

    try:
        response = requests.get(url, timeout=10)

        print(f"HTTP: {response.status_code}")

        if response.status_code != 200:
            print("❌ No se encontraron lyrics.")
            print(response.text)
            return None

        data = response.json()

        lyrics = data.get("lyrics")

        if not lyrics:
            print("❌ La API respondió pero no entregó lyrics.")
            return None

        return lyrics

    except requests.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return None


def main():

    if len(sys.argv) != 3:
        print("Uso:")
        print("  lyrics_test.py \"Artista\" \"Título\"")
        print()
        print("Ejemplo:")
        print('  lyrics_test.py "Steve Perry" "Oh Sherrie"')
        sys.exit(1)

    artist = sys.argv[1]
    title = sys.argv[2]

    print("=" * 70)
    print("PRUEBA DE BÚSQUEDA DE LYRICS")
    print("=" * 70)
    print(f"Artista : {artist}")
    print(f"Título  : {title}")
    print("-" * 70)

    lyrics = search_lyrics(artist, title)

    if lyrics:
        print()
        print("✅ LETRA ENCONTRADA")
        print("=" * 70)
        print(lyrics)
        print("=" * 70)
        print(f"\nCaracteres: {len(lyrics)}")


if __name__ == "__main__":
    main()
