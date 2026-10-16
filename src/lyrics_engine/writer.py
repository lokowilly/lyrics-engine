
import shutil
from pathlib import Path

from mutagen.flac import FLAC
from mutagen.id3 import ID3, USLT

from .models import LyricsResult


def create_backup(audio_path):
    """
    Crea una copia .bak del archivo de audio.
    Nunca sobrescribe un backup existente.
    """

    audio_path = Path(audio_path)
    backup_path = audio_path.with_suffix(
        audio_path.suffix + ".bak"
    )

    if backup_path.exists():
        return backup_path

    shutil.copy2(audio_path, backup_path)

    return backup_path


def write_lyrics(
    audio_path,
    lyrics,
    language="eng",
    description="Lyrics",
    overwrite=False,
):
    """
    Escribe letras en archivos MP3 o FLAC.

    MP3:
        Usa el frame ID3 USLT.

    FLAC:
        Usa el comentario Vorbis LYRICS.

    Antes de modificar:
    - comprueba si ya existen letras
    - crea un backup .bak
    - no sobrescribe letras existentes si overwrite=False
    """

    audio_path = Path(audio_path)
    extension = audio_path.suffix.lower()

    try:
        if extension == ".mp3":
            audio = ID3(audio_path)
            existing = audio.getall("USLT")

            if existing and not overwrite:
                return LyricsResult(
                    status="ALREADY_EXISTS",
                    message="El archivo ya contiene lyrics.",
                )

            backup_path = create_backup(audio_path)

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

            audio.save(audio_path, v2_version=3)

        elif extension == ".flac":
            audio = FLAC(audio_path)
            existing = audio.get("LYRICS", [])

            if existing and not overwrite:
                return LyricsResult(
                    status="ALREADY_EXISTS",
                    message="El archivo ya contiene lyrics.",
                )

            backup_path = create_backup(audio_path)

            if overwrite:
                audio.pop("LYRICS", None)

            audio["LYRICS"] = [lyrics]
            audio.save()

        else:
            return LyricsResult(
                status="ERROR",
                message=f"Formato no compatible: {extension}",
            )

        return LyricsResult(
            status="WRITTEN",
            message=f"Lyrics guardadas. Backup: {backup_path}",
        )

    except Exception as e:
        return LyricsResult(
            status="ERROR",
            message=f"Error escribiendo lyrics: {e}",
        )
