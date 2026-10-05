class LyricsResult:
    def __init__(
        self,
        status,
        artist=None,
        title=None,
        lyrics=None,
        source=None,
        message=None,
        variant=None,
        query_title=None,
        attempt=None,
    ):
        self.status = status
        self.artist = artist
        self.title = title
        self.lyrics = lyrics
        self.source = source
        self.message = message
        self.variant = variant
        self.query_title = query_title
        self.attempt = attempt
