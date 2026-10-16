
from pathlib import Path

from mutagen.flac import FLAC
from mutagen.id3 import ID3

from .models import LyricsResult


def get_metadata(audio_path):
    """
    Lee artista y título desde los tags del archivo.
    Compatible con MP3 y FLAC.
    No modifica el archivo.
    """

    audio_path = Path(audio_path)

    try:
        if audio_path.suffix.lower() == ".mp3":
            audio = ID3(audio_path)
            artist = audio.get("TPE1")
            title = audio.get("TIT2")

        elif audio_path.suffix.lower() == ".flac":
            audio = FLAC(audio_path)
            artist = audio.get("ARTIST")
            title = audio.get("TITLE")

            # Los comentarios Vorbis pueden contener listas.
            artist = artist[0] if artist else None
            title = title[0] if title else None

        else:
            return LyricsResult(
                status="ERROR",
                message=f"Formato no compatible: {audio_path.suffix}",
            )

        artist = str(artist) if artist else None
        title = str(title) if title else None

        if not artist or not title:
            return LyricsResult(
                status="ERROR",
                message="No se pudo obtener artista/título desde los tags.",
            )

        return LyricsResult(
            status="OK",
            artist=artist,
            title=title,
        )

    except Exception as e:
        return LyricsResult(
            status="ERROR",
            message=f"Error leyendo metadata: {e}",
        )


def read_existing_lyrics(audio_path):
    """
    Devuelve las letras existentes.
    MP3: frames ID3 USLT.
    FLAC: comentario Vorbis LYRICS.
    No modifica el archivo.
    """

    audio_path = Path(audio_path)

    try:
        if audio_path.suffix.lower() == ".mp3":
            audio = ID3(audio_path)
            return audio.getall("USLT")

        elif audio_path.suffix.lower() == ".flac":
            audio = FLAC(audio_path)
            return audio.get("LYRICS", [])

        return []

    except Exception:
        return []
