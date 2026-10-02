#!/usr/bin/env python3

import shutil
import sys
from pathlib import Path
from urllib.parse import quote

import requests
from mutagen.id3 import ID3, USLT


def get_lyrics(artist, title):
    """Obtiene la letra desde lyrics.ovh."""

    url = (
        f"https://api.lyrics.ovh/v1/"
        f"{quote(artist)}/"
        f"{quote(title)}"
    )

    print(f"Consultando: {url}")

    try:
        response = requests.get(url, timeout=15)

        print(f"HTTP: {response.status_code}")

        if response.status_code != 200:
            print("❌ No se encontraron lyrics.")
            return None

        data = response.json()
        lyrics = data.get("lyrics")

        if not lyrics:
            print("❌ La API no entregó lyrics.")
            return None

        return lyrics.strip()

    except requests.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return None


def write_lyrics(mp3_path, lyrics):
    """Escribe lyrics en un MP3 usando ID3 USLT."""

    path = Path(mp3_path)
    backup = Path(str(path) + ".bak")

    print()
    print("Archivo :", path)
    print("Backup  :", backup)

    # Crear backup
    if not backup.exists():
        shutil.copy2(path, backup)
        print("✅ Backup creado.")
    else:
        print("ℹ️ El backup ya existe. No se sobrescribe.")

    # Abrir tags ID3 existentes
    try:
        tags = ID3(path)
    except Exception as e:
        print(f"❌ No se pudieron abrir los tags ID3: {e}")
        return False

    # Eliminar únicamente nuestro USLT en inglés
    tags.delall("USLT")

    # Agregar lyrics
    tags.add(
        USLT(
            encoding=3,
            lang="eng",
            desc="Lyrics",
            text=lyrics
        )
    )

    # Guardar
    try:
        tags.save(path, v2_version=3)
    except Exception as e:
        print(f"❌ Error guardando el archivo: {e}")
        return False

    print("✅ Lyrics escritos correctamente.")
    return True


def main():

    if len(sys.argv) != 2:
        print("Uso:")
        print("  lyrics_write_test.py archivo.mp3")
        sys.exit(1)

    path = Path(sys.argv[1])

    if not path.is_file():
        print(f"❌ No existe el archivo: {path}")
        sys.exit(1)

    print("=" * 70)
    print("PRUEBA DE ESCRITURA DE LYRICS")
    print("=" * 70)

    # Leer metadata
    try:
        tags = ID3(path)

        artist = tags.get("TPE1")
        title = tags.get("TIT2")

        if not artist or not title:
            print("❌ El MP3 no tiene artista o título.")
            sys.exit(1)

        artist = str(artist)
        title = str(title)

    except Exception as e:
        print(f"❌ Error leyendo metadata: {e}")
        sys.exit(1)

    print(f"Artista : {artist}")
    print(f"Título  : {title}")

    # Buscar lyrics
    lyrics = get_lyrics(artist, title)

    if not lyrics:
        sys.exit(1)

    print()
    print("-" * 70)
    print("LETRA ENCONTRADA")
    print("-" * 70)
    print(lyrics)
    print("-" * 70)
    print(f"Caracteres: {len(lyrics)}")

    # Confirmación
    print()
    respuesta = input(
        "¿Escribir esta letra en el MP3? [s/N]: "
    ).strip().lower()

    if respuesta != "s":
        print("❌ Operación cancelada. El MP3 no fue modificado.")
        sys.exit(0)

    # Escribir
    if write_lyrics(path, lyrics):
        print()
        print("=" * 70)
        print("✅ OPERACIÓN COMPLETADA")
        print("=" * 70)
    else:
        print("❌ No se pudo completar la operación.")
        sys.exit(1)


if __name__ == "__main__":
    main()
