#!/usr/bin/env python3

from pathlib import Path

from lyrics_engine import (
    get_metadata,
    read_existing_lyrics,
    search_lyrics,
    write_lyrics,
)


MP3 = Path(
    "~/Descargas/Musica/"
    "1998 - Greatest Hits -Steve Perry/"
    "01 - Oh Sherrie.mp3"
).expanduser()


print("=" * 70)
print("PRUEBA DEL LYRICS ENGINE")
print("=" * 70)


# ------------------------------------------------------------
# 1. Metadata
# ------------------------------------------------------------

print()
print("[1] LEYENDO METADATA")

metadata = get_metadata(MP3)

print(f"Artista : {metadata['artist']}")
print(f"Título  : {metadata['title']}")


# ------------------------------------------------------------
# 2. Lyrics existentes
# ------------------------------------------------------------

print()
print("[2] BUSCANDO LYRICS EXISTENTES")

existing = read_existing_lyrics(MP3)

print(f"USLT encontrados: {len(existing)}")

for i, item in enumerate(existing, 1):
    print(
        f"  #{i}: "
        f"idioma={item['language']} "
        f"descripción={item['description']} "
        f"caracteres={len(item['text'])}"
    )


# ------------------------------------------------------------
# 3. Buscar en Internet
# ------------------------------------------------------------

print()
print("[3] BUSCANDO LYRICS")

result = search_lyrics(
    metadata["artist"],
    metadata["title"],
)

print(f"Estado : {result.status}")
print(f"Fuente : {result.source}")

if result.message:
    print(f"Mensaje: {result.message}")

if result.lyrics:
    print(f"Caracteres encontrados: {len(result.lyrics)}")


# ------------------------------------------------------------
# 4. Intentar escribir SIN overwrite
# ------------------------------------------------------------

print()
print("[4] PRUEBA DE PROTECCIÓN")

if result.lyrics:

    write_result = write_lyrics(
        MP3,
        result.lyrics,
        overwrite=False,
    )

    print(f"Estado : {write_result['status']}")
    print(f"Mensaje: {write_result['message']}")

else:
    print("No hay lyrics para escribir.")


print()
print("=" * 70)
print("FIN DE LA PRUEBA")
print("=" * 70)
