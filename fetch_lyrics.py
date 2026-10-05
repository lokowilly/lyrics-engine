#!/usr/bin/env python3

import argparse
from pathlib import Path

from lyrics_engine import search_lyrics
from lyrics_engine.metadata import (
    get_metadata,
    read_existing_lyrics,
)
from lyrics_engine.writer import write_lyrics


SUPPORTED_EXTENSIONS = {
    ".mp3",
}


def find_audio_files(folder):
    """Busca archivos de audio compatibles."""

    files = []

    for path in folder.rglob("*"):
        if not path.is_file():
            continue

        if path.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(path)

    return sorted(files)


def process_file(path, mode, overwrite=False):
    """
    Procesa un archivo individual.

    Devuelve el estado final.
    """

    print()
    print("=" * 70)
    print(f"ARCHIVO: {path.name}")
    print(f"RUTA   : {path}")
    print("=" * 70)

    # --------------------------------------------------------
    # 1. Metadata
    # --------------------------------------------------------

    try:
        metadata = get_metadata(path)

    except Exception as e:
        print(f"❌ Error leyendo metadata: {e}")
        return "ERROR"

    if metadata.status != "OK":
        print(f"❌ Error leyendo metadata: {metadata.message}")
        return "ERROR"

    artist = metadata.artist
    title = metadata.title

    print(f"Artista : {artist}")
    print(f"Título  : {title}")

    # --------------------------------------------------------
    # 2. Lyrics existentes
    # --------------------------------------------------------

    try:
        existing = read_existing_lyrics(path)

    except Exception as e:
        print(f"❌ Error leyendo lyrics existentes: {e}")
        return "ERROR"

    if existing and not overwrite:

        print()
        print("⏭️  Ya contiene lyrics.")
        print(f"    USLT encontrados: {len(existing)}")

        return "ALREADY_EXISTS"

    if existing and overwrite:

        print()
        print("⚠️  Tiene lyrics existentes.")
        print("    Se permitirá reemplazarlas.")

    # --------------------------------------------------------
    # 3. Buscar lyrics
    # --------------------------------------------------------

    print()
    print("🔎 Buscando lyrics...")

    result = search_lyrics(
        artist,
        title,
    )

    print(f"Estado : {result.status}")

    if result.attempt:
        print(f"Intento: {result.attempt}")

    if result.source:
        print(f"Fuente : {result.source}")

    if result.variant:
        print(f"Regla  : {result.variant}")

    if result.query_title:
        print(f"Consulta: {result.query_title}")

    if result.message:
        print(f"Mensaje: {result.message}")

    if result.status != "FOUND":
        return result.status

    print(f"Caracteres encontrados: {len(result.lyrics)}")
    

    # --------------------------------------------------------
    # 4. DRY-RUN
    # --------------------------------------------------------

    if mode == "dry-run":

        print()
        print("🟡 DRY-RUN")
        print("    No se modificará el archivo.")

        return "FOUND"

    # --------------------------------------------------------
    # 5. REVIEW
    # --------------------------------------------------------

    if mode == "review":

        print()
        print("-" * 70)
        print("PRIMEROS 500 CARACTERES")
        print("-" * 70)
        print(result.lyrics[:500])

        if len(result.lyrics) > 500:
            print("...")
        
        print("-" * 70)

        answer = input(
            "¿Escribir estas lyrics? [s/N]: "
        ).strip().lower()

        if answer != "s":

            print("⏭️  Usuario canceló este archivo.")

            return "SKIPPED"

    # --------------------------------------------------------
    # 6. AUTO / REVIEW confirmado
    # --------------------------------------------------------

    print()
    print("💾 Escribiendo lyrics...")

    try:

        write_result = write_lyrics(
            path,
            result.lyrics,
            overwrite=overwrite,
        )

    except Exception as e:

        print(f"❌ Error escribiendo: {e}")

        return "ERROR"

    print(f"Estado escritura: {write_result.status}")

    if write_result.message:
        print(f"Mensaje: {write_result.message}")

    return write_result.status

def main():

    parser = argparse.ArgumentParser(
        description="Lyrics Engine para bibliotecas musicales."
    )

    parser.add_argument(
        "folder",
        help="Carpeta que contiene música.",
    )

    mode_group = parser.add_mutually_exclusive_group(
        required=True
    )

    mode_group.add_argument(
        "--dry-run",
        action="store_true",
        help="Buscar lyrics sin modificar archivos.",
    )

    mode_group.add_argument(
        "--review",
        action="store_true",
        help="Preguntar antes de escribir cada archivo.",
    )

    mode_group.add_argument(
        "--auto",
        action="store_true",
        help="Escribir automáticamente.",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Permitir reemplazar lyrics existentes.",
    )

    args = parser.parse_args()

    folder = Path(args.folder).expanduser()

    if not folder.is_dir():

        print(f"❌ La carpeta no existe: {folder}")

        raise SystemExit(1)

    # Determinar modo
    if args.dry_run:
        mode = "dry-run"

    elif args.review:
        mode = "review"

    else:
        mode = "auto"

    print("=" * 70)
    print("LYRICS ENGINE")
    print("=" * 70)

    print(f"Carpeta : {folder}")
    print(f"Modo    : {mode}")

    if args.overwrite:
        print("⚠️ OVERWRITE: activado")
    else:
        print("Protección contra sobrescritura: activada")

    print()
    print("Buscando archivos...")

    files = find_audio_files(folder)

    print(f"Archivos MP3 encontrados: {len(files)}")

    if not files:

        print("No hay archivos MP3.")
        return

    # --------------------------------------------------------
    # Estadísticas
    # --------------------------------------------------------

    stats = {
        "FOUND": 0,
        "WRITTEN": 0,
        "ALREADY_EXISTS": 0,
        "NOT_FOUND": 0,
        "ERROR": 0,
        "SKIPPED": 0,
    }

    # --------------------------------------------------------
    # Procesamiento
    # --------------------------------------------------------

    for path in files:

        status = process_file(
            path,
            mode,
            overwrite=args.overwrite,
        )

        if status in stats:
            stats[status] += 1

    # --------------------------------------------------------
    # Resumen
    # --------------------------------------------------------

    print()
    print()
    print("=" * 70)
    print("RESUMEN")
    print("=" * 70)

    print(f"Archivos encontrados : {len(files)}")
    print(f"Lyrics encontradas   : {stats['FOUND']}")
    print(f"Lyrics escritas      : {stats['WRITTEN']}")
    print(f"Ya tenían lyrics     : {stats['ALREADY_EXISTS']}")
    print(f"No encontradas       : {stats['NOT_FOUND']}")
    print(f"Saltadas             : {stats['SKIPPED']}")
    print(f"Errores              : {stats['ERROR']}")

    print()

    if mode == "dry-run":

        print("🟡 DRY-RUN")
        print("No se modificó ningún archivo.")

    else:

        print("✅ PROCESAMIENTO FINALIZADO")


if __name__ == "__main__":
    main()
