#!/usr/bin/env python3

import sys
from pathlib import Path

from mutagen import File


def get_first(tags, *names):
    """Devuelve el primer valor encontrado entre varios nombres de tag."""
    if not tags:
        return None

    for name in names:
        value = tags.get(name)
        if value:
            if isinstance(value, list):
                return str(value[0])
            return str(value)

    return None


def show_info(filepath):
    path = Path(filepath)

    if not path.is_file():
        print(f"❌ No existe el archivo: {filepath}")
        return 1

    print("=" * 70)
    print("INFORMACIÓN DEL ARCHIVO MUSICAL")
    print("=" * 70)

    print(f"Archivo : {path.name}")
    print(f"Ruta    : {path}")
    print(f"Tamaño  : {path.stat().st_size / 1024 / 1024:.2f} MB")
    print(f"Formato : {path.suffix.lower()}")

    try:
        audio = File(path, easy=False)

        if audio is None:
            print("\n❌ Mutagen no reconoce este archivo.")
            return 1

        print(f"Duración: {audio.info.length:.2f} segundos")

        if hasattr(audio.info, "bitrate"):
            bitrate = audio.info.bitrate
            if bitrate:
                print(f"Bitrate : {bitrate // 1000} kbps")

        tags = audio.tags

        if not tags:
            print("\n⚠️ El archivo no tiene tags.")
            return 0

        print("\n" + "-" * 70)
        print("DATOS MUSICALES")
        print("-" * 70)

        # MP3 / ID3
        artist = get_first(tags, "TPE1", "artist")
        title = get_first(tags, "TIT2", "title")
        album = get_first(tags, "TALB", "album")
        album_artist = get_first(tags, "TPE2", "albumartist")
        year = get_first(tags, "TDRC", "date")
        genre = get_first(tags, "TCON", "genre")
        track = get_first(tags, "TRCK", "tracknumber")
        disc = get_first(tags, "TPOS", "discnumber")
        isrc = get_first(tags, "TSRC", "isrc")

        # FLAC / OGG / otros Vorbis
        if not artist:
            artist = get_first(tags, "artist")
        if not title:
            title = get_first(tags, "title")
        if not album:
            album = get_first(tags, "album")
        if not album_artist:
            album_artist = get_first(tags, "albumartist")
        if not year:
            year = get_first(tags, "date")
        if not genre:
            genre = get_first(tags, "genre")
        if not track:
            track = get_first(tags, "tracknumber")
        if not disc:
            disc = get_first(tags, "discnumber")
        if not isrc:
            isrc = get_first(tags, "isrc", "ISRC")

        print(f"Artista       : {artist or '—'}")
        print(f"Título        : {title or '—'}")
        print(f"Álbum         : {album or '—'}")
        print(f"Artista álbum : {album_artist or '—'}")
        print(f"Año           : {year or '—'}")
        print(f"Género        : {genre or '—'}")
        print(f"Pista         : {track or '—'}")
        print(f"Disco         : {disc or '—'}")
        print(f"ISRC          : {isrc or '—'}")

        print("\n" + "-" * 70)
        print("TAGS DETECTADOS")
        print("-" * 70)

        for key in tags.keys():
            print(key)

        print("=" * 70)

        return 0

    except Exception as e:
        print(f"\n❌ Error leyendo el archivo:")
        print(f"   {e}")
        return 1


def main():
    if len(sys.argv) != 2:
        print("Uso:")
        print("  music_info.py archivo.mp3")
        print()
        print("Ejemplo:")
        print("  music_info.py ~/Música/cancion.mp3")
        sys.exit(1)

    sys.exit(show_info(sys.argv[1]))


if __name__ == "__main__":
    main()
