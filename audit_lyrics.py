#!/usr/bin/env python3

from pathlib import Path
from mutagen.id3 import ID3


def audit_folder(folder):
    folder = Path(folder)

    if not folder.is_dir():
        print(f"❌ No existe la carpeta: {folder}")
        return 1

    files = sorted(folder.glob("*.mp3"))

    print("=" * 110)
    print("AUDITORÍA DE LYRICS / USLT")
    print("=" * 110)
    print(f"Carpeta: {folder}")
    print(f"Archivos MP3: {len(files)}")
    print()

    header = (
        f"{'ARCHIVO':<48}"
        f"{'USLT':>6} "
        f"{'IDIOMA':<8}"
        f"{'DESC':<12}"
        f"{'CARACTERES':>12}"
        f"{'ESTADO':<15}"
    )

    print(header)
    print("-" * 110)

    total_uslt = 0
    total_chars = 0
    files_with_lyrics = 0
    files_without_lyrics = 0
    files_with_duplicates = 0
    errors = 0

    for mp3 in files:

        try:
            audio = ID3(mp3)
            uslt = audio.getall("USLT")

            count = len(uslt)
            total_uslt += count

            if count == 0:
                files_without_lyrics += 1

                print(
                    f"{mp3.name[:47]:<48}"
                    f"{0:>6} "
                    f"{'-':<8}"
                    f"{'-':<12}"
                    f"{0:>12}"
                    f"{'SIN LYRICS':<15}"
                )

                continue

            files_with_lyrics += 1

            if count > 1:
                files_with_duplicates += 1

            # Tomamos información del primer USLT
            frame = uslt[0]

            language = frame.lang or "-"
            description = frame.desc or "-"
            chars = len(frame.text or "")

            total_chars += chars

            if count > 1:
                estado = "⚠ DUPLICADO"
            elif chars == 0:
                estado = "⚠ VACÍA"
            else:
                estado = "OK"

            print(
                f"{mp3.name[:47]:<48}"
                f"{count:>6} "
                f"{language:<8}"
                f"{description[:11]:<12}"
                f"{chars:>12}"
                f"{estado:<15}"
            )

        except Exception as e:

            errors += 1

            print(
                f"{mp3.name[:47]:<48}"
                f"{'-':>6} "
                f"{'-':<8}"
                f"{'-':<12}"
                f"{'-':>12}"
                f"{'ERROR':<15}"
            )

            print(f"    → {e}")

    print()
    print("=" * 110)
    print("RESUMEN")
    print("=" * 110)

    print(f"Archivos MP3             : {len(files)}")
    print(f"Archivos con USLT        : {files_with_lyrics}")
    print(f"Archivos sin USLT        : {files_without_lyrics}")
    print(f"Frames USLT totales      : {total_uslt}")
    print(f"Archivos con duplicados  : {files_with_duplicates}")
    print(f"Caracteres totales       : {total_chars}")
    print(f"Errores                  : {errors}")

    print()

    if (
        len(files) == 18
        and files_with_lyrics == 18
        and files_with_duplicates == 0
        and errors == 0
    ):
        print("✅ AUDITORÍA PERFECTA: 18/18 archivos con un único USLT.")
    else:
        print("⚠️ La auditoría encontró elementos que debemos revisar.")

    print("=" * 110)

    return 0


if __name__ == "__main__":

    import sys

    if len(sys.argv) != 2:
        print(
            "Uso:\n"
            "  python audit_lyrics.py /ruta/a/carpeta"
        )
        sys.exit(1)

    sys.exit(audit_folder(sys.argv[1]))
