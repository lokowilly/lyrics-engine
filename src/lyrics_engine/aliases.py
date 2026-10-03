def get_artist_aliases(artist, title):
    """
    Devuelve el artista original y cualquier alias especial
    necesario para buscar la canción en los proveedores.

    No modifica archivos MP3.
    """

    artist_aliases = [
        artist,
    ]

    special_artist_aliases = {
        (
            "steve perry",
            "don't fight it",
        ): [
            "Kenny Loggins & Steve Perry",
        ],
    }

    alias_key = (
        artist.strip().lower(),
        title.strip().lower(),
    )

    if alias_key in special_artist_aliases:
        artist_aliases.extend(
            special_artist_aliases[alias_key]
        )

    return artist_aliases
