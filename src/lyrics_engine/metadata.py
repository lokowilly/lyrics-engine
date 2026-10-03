from mutagen.id3 import ID3

from .models import LyricsResult


def get_metadata(mp3_path):
    """
    Lee artista y título desde los tags ID3.
    No modifica el archivo.
    """

    try:
        audio = ID3(mp3_path)

        artist = audio.get("TPE1")
        title = audio.get("TIT2")

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


def read_existing_lyrics(mp3_path):
    """
    Devuelve los frames USLT existentes.
    No modifica el archivo.
    """

    try:
        audio = ID3(mp3_path)

        return audio.getall("USLT")

    except Exception:
        return []
