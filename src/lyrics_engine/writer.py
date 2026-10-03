import shutil
from pathlib import Path

from mutagen.id3 import ID3, USLT

from .models import LyricsResult


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
