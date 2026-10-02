#!/usr/bin/env python3

import sys
from pathlib import Path
from mutagen.id3 import ID3


def main():

    if len(sys.argv) != 2:
        print("Uso:")
        print("  read_lyrics.py archivo.mp3")
        sys.exit(1)

    path = Path(sys.argv[1])

    if not path.is_file():
        print(f"❌ No existe: {path}")
        sys.exit(1)

    try:
        tags = ID3(path)
    except Exception as e:
        print(f"❌ Error leyendo ID3: {e}")
        sys.exit(1)

    print("=" * 70)
    print("VERIFICACIÓN DE LYRICS")
    print("=" * 70)

    print(f"Archivo : {path.name}")
    print()

    # Metadata importante
    print("-" * 70)
    print("METADATA")
    print("-" * 70)

    for frame, nombre in [
        ("TPE1", "Artista"),
        ("TIT2", "Título"),
        ("TALB", "Álbum"),
        ("TPE2", "Artista álbum"),
        ("TDRC", "Año"),
        ("TCON", "Género"),
        ("TRCK", "Pista"),
        ("TBPM", "BPM"),
    ]:
        value = tags.get(frame)

        if value:
            print(f"{nombre:15}: {value}")

    # Portada
    apic = tags.getall("APIC")
    print(f"{'Portadas APIC':15}: {len(apic)}")

    # Comentarios
    comm = tags.getall("COMM")
    print(f"{'Comentarios':15}: {len(comm)}")

    # Lyrics
    uslt = tags.getall("USLT")

    print()
    print("-" * 70)
    print("LYRICS / USLT")
    print("-" * 70)

    print(f"Frames USLT: {len(uslt)}")

    if not uslt:
        print("❌ No se encontraron lyrics.")
        sys.exit(1)

    for i, frame in enumerate(uslt, 1):

        print()
        print(f"LYRICS #{i}")
        print(f"Idioma     : {frame.lang}")
        print(f"Descripción: {frame.desc}")
        print(f"Caracteres : {len(frame.text)}")
        print("-" * 70)
        print(frame.text)
        print("-" * 70)

    print()
    print("=" * 70)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("=" * 70)


if __name__ == "__main__":
    main()
