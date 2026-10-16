# Lyrics Engine Architecture

## Overview

Lyrics Engine is a modular Python library for searching and retrieving song lyrics and safely storing them in MP3 and FLAC files.

The core engine is independent from any specific music application. This allows the same functionality to be used from a command-line tool, a future Puddletag integration, or other applications.

The architecture separates:

- Search orchestration and retry handling
- Result representation
- Artist aliases and title variants
- Independent lyrics providers
- Audio metadata reading (MP3 and FLAC)
- Lyrics writing and file protection

The search engine tries four providers in sequence. If the first complete search attempt does not find lyrics, it waits one second and performs one more complete attempt.

```text
Artist and title
       |
       v
    engine.py
       |
       +--> Artist aliases and title variants
       |
       v
    lyrics.ovh
       |
       | Not found
       v
    LyricsWeb
       |
       | Not found
       v
    Lyrics.com
       |
       | Not found
       v
     LRCLIB
       |
       v
   LyricsResult
```

A successful result stops the search. If neither complete attempt finds lyrics, the engine returns `NOT_FOUND` or `ERROR`, depending on the provider results.

---

## Project Structure

```text
lyrics-engine/
├── fetch_lyrics.py
├── pyproject.toml
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CHANGELOG.md
├── docs/
│   └── ARCHITECTURE.md
├── src/
│   └── lyrics_engine/
│       ├── __init__.py
│       ├── aliases.py
│       ├── engine.py
│       ├── metadata.py
│       ├── models.py
│       ├── title_variants.py
│       ├── writer.py
│       └── providers/
│           ├── __init__.py
│           ├── lyrics_ovh.py
│           ├── lyricsweb.py
│           ├── lyrics_com.py
│           └── lrclib.py
└── tests/
    └── ...
```


# Core Components

## `engine.py`

The engine is the main orchestration layer. It coordinates the lyrics search process without implementing provider-specific HTTP logic or modifying audio files.

The main public function is:

```python
search_lyrics(artist, title)
```

During each complete search attempt, the engine performs the following operations:

1. Receives the artist and title.
2. Obtains possible artist aliases using `get_artist_aliases()`.
3. Generates title variants using `generate_title_variants()` for searches with lyrics.ovh.
4. Searches lyrics.ovh using artist aliases and title variants.
5. Searches LyricsWeb using artist aliases.
6. Searches Lyrics.com.
7. Searches LRCLIB.
8. Returns the first valid result as a `LyricsResult`.

If no provider returns lyrics during the first attempt, the engine waits one second and repeats the complete search once. Therefore, it performs at most two complete search attempts.

If no lyrics are found after both attempts, the engine returns `ERROR` when all four providers report the `ERROR` status. Otherwise, it returns `NOT_FOUND`.

The engine does not write lyrics to audio files. Searching for lyrics and modifying audio files are independent operations.

---

## `models.py`

`models.py` contains the common result model used throughout the project.

The main class is:

```python
LyricsResult
```

It provides a common structure for successful searches, failures and other processing results.

The model currently supports:

```text
status
artist
title
lyrics
source
message
variant
query_title
```

This allows different providers and internal components to communicate using the same result format.

For example:

```python
LyricsResult(
    status="FOUND",
    artist="Steve Perry",
    title="She's Mine",
    lyrics="...",
    source="lyrics.ovh",
)
```

Using a common result model prevents each provider from inventing its own return format.

---

# Search Preparation

## `aliases.py`

`aliases.py` handles artist aliases.

The function:

```python
get_artist_aliases(artist, title)
```

returns the original artist plus any known alternative artist names required for a specific song.

For example, the project currently contains a special case for:

```text
Steve Perry
Don't Fight It
```

which can also be searched as:

```text
Kenny Loggins & Steve Perry
```

The alias system is deliberately separate from the providers.

Providers therefore do not need to know why an alternative artist name is being used.

---

## `title_variants.py`

`title_variants.py` generates alternative forms of a song title.

The function:

```python
generate_title_variants(title)
```

currently handles several transformations:

1. Original title
2. Removal of apostrophes
3. Conversion of dashes to spaces
4. Removal of parenthetical text
5. Removal of parenthetical text plus apostrophes
6. Unicode normalization
7. Unicode normalization plus apostrophe removal

Example:

```text
When You're In Love (For the First Time)
```

may generate variants such as:

```text
When You're In Love (For the First Time)
When Youre In Love (For the First Time)
When You're In Love
When Youre In Love
```

Duplicates are removed while preserving the original order.

The title variant generator does not perform network requests and does not modify audio files.

---

# Lyrics Providers

Providers are located under:

```text
src/lyrics_engine/providers/
```

Each provider is responsible for communicating with one external lyrics source.

The provider receives a prepared artist and title and returns a `LyricsResult`.

Providers do not generate title variants or artist aliases.

This keeps the provider implementations simple and independently testable.

---

## `providers/lyrics_ovh.py`

This module implements the lyrics.ovh provider.

The main function is:

```python
search_lyrics_ovh(artist, title)
```

The provider:

1. Builds the lyrics.ovh API URL.
2. URL-encodes the artist and title.
3. Performs an HTTP request.
4. Handles connection errors.
5. Handles unsuccessful HTTP responses.
6. Parses the JSON response.
7. Extracts the `lyrics` field.
8. Returns a `LyricsResult`.

The provider uses a request timeout to prevent the application from waiting indefinitely.

The provider does not:

- Generate title variants
- Generate artist aliases
- Modify audio files

Those responsibilities belong to other modules.

---

## `providers/lyricsweb.py`

This module implements the LyricsWeb fallback provider.

The main function is:

```python
search_lyrics_lyricsweb(artist, title)
```

The provider:

1. Builds a LyricsWeb URL.
2. Handles known special URLs where necessary.
3. Generates a URL slug for normal requests.
4. Performs the HTTP request.
5. Checks the HTTP response.
6. Locates the `lyrics-panel` section.
7. Converts HTML line breaks into text line breaks.
8. Removes remaining HTML tags.
9. Decodes HTML entities.
10. Cleans the resulting text.
11. Returns a `LyricsResult`.

LyricsWeb is used as a fallback after lyrics.ovh has failed to find the requested lyrics.

The provider does not modify audio files.

---

## `providers/lyrics_com.py`

This module implements the Lyrics.com provider.

The main search function is:

```python
search_lyrics_com(artist, title)
```

The provider:

1. Builds a search URL using the supplied artist and title.
2. Performs an HTTP request with a 20-second timeout.
3. Extracts candidate links pointing to Lyrics.com lyric pages.
4. Accepts only links hosted on Lyrics.com with supported lyric URL paths.
5. Compares the candidate artist and title with the requested metadata after normalizing case, punctuation and whitespace.
6. Downloads and parses the selected lyric page.
7. Validates the artist and title shown on the page.
8. Extracts the lyrics from the `pre#lyric-body-text` element.
9. Converts HTML line breaks, removes HTML tags and decodes HTML entities.
10. Returns a `LyricsResult`.

The module also provides `parse_lyrics_page()`, which parses supplied HTML without making a network request, and `search_lyrics_lyrics_com()`, which downloads and parses a specific URL.

Lyrics.com is called after LyricsWeb by the engine. It receives the original artist and title, rather than the aliases and title variants used by the first two providers.

The provider does not modify audio files.

---

## `providers/lrclib.py`

This module implements the LRCLIB API provider.

The main function is:

```python
search_lyrics_lrclib(artist, title)
```

The provider:

1. Queries the LRCLIB search API using the supplied artist and title.
2. Sends a User-Agent header and uses a 15-second timeout.
3. Handles connection errors, rate limiting, server errors and unexpected HTTP responses.
4. Parses the JSON response and validates its structure.
5. Compares candidate artist and title metadata after normalizing case, accents, punctuation and whitespace.
6. Prefers non-empty `plainLyrics` when available.
7. If plain lyrics are unavailable, converts `syncedLyrics` into plain text by removing leading timestamp markers.
8. Returns the first exact metadata match that contains usable lyrics as a `LyricsResult`.

LRCLIB is called after Lyrics.com by the engine and receives the original artist and title.

The provider does not modify audio files or log lyric content.

# Audio Metadata

## `metadata.py`

`metadata.py` is responsible for reading artist, title and existing lyrics metadata from supported audio files: MP3 and FLAC.

It currently provides two main functions:

```python
get_metadata(audio_path)
```

and:

```python
read_existing_lyrics(audio_path)
```

### `get_metadata()`

The metadata format depends on the file type.

For MP3 files, it reads the ID3 artist and title frames:

```text
TPE1 → Artist
TIT2 → Title
```

For FLAC files, it reads Vorbis comments:

```text
ARTIST → Artist
TITLE  → Title
```

The function does not modify the audio file.

It returns a `LyricsResult` containing the artist and title when successful.

If the required metadata cannot be read, an `ERROR` result is returned.

### `read_existing_lyrics()`

This function reads existing lyrics without modifying the audio file.

For MP3, it reads ID3 `USLT` frames.

For FLAC, it reads the `LYRICS` Vorbis comment.

If the file cannot be read, the function returns an empty list rather than modifying or damaging the file.

Keeping metadata reading separate from the search engine allows the engine to operate independently of a particular audio format.

---

# Lyrics Writing

## `writer.py`

`writer.py` contains the functionality that writes lyrics to supported MP3 and FLAC files.

This module is deliberately separated from the search engine.

The main functions include:

```python
create_backup(audio_path)
```

and:

```python
write_lyrics(...)
```

---

## Backup Protection

Before modifying an audio file, the writer creates a backup using the original filename with `.bak` appended.

Examples:

```text
filename.mp3.bak
filename.flac.bak
```

An existing backup is not overwritten.

This provides a recovery point before changing the original file.

---

## Format-Specific Lyrics Writing

The lyrics are stored differently depending on the audio format.

For MP3, the writer uses ID3 `USLT` frames and saves the file using ID3 version 2.3.

For FLAC, the writer stores the lyrics in the `LYRICS` Vorbis comment.

The writer checks for existing lyrics before writing. By default, existing lyrics are protected unless overwrite is explicitly enabled.

## Explicit Overwrite

When:

```python
overwrite=True
```

the writer explicitly replaces existing lyrics in the supported audio format.

For MP3 files, existing ID3 `USLT` frames are removed before the new lyrics are written.

For FLAC files, the existing `LYRICS` Vorbis comment is removed before the new lyrics are stored.

This makes overwriting an explicit operation rather than an accidental side effect.

---

## MP3 USLT Writing

For MP3 files, lyrics are stored in an ID3 `USLT` frame.

The current implementation uses:

```text
language = eng
description = Lyrics
encoding = 3
```

The file is saved using ID3 version 2.3.

---

## Write Results

The writer returns:

```text
WRITTEN
```

when the operation succeeds.

If lyrics already exist and `overwrite=False`, it returns:

```text
ALREADY_EXISTS
```

without replacing them.

If an exception occurs, it returns:

```text
ERROR
```

with an explanatory message.

For FLAC files, lyrics are stored in the `LYRICS` Vorbis comment rather than an ID3 `USLT` frame.

# Separation of Responsibilities

A key design principle of Lyrics Engine is that each component has one primary responsibility.

| Component | Responsibility |
|---|---|
| `engine.py` | Search orchestration and retry handling |
| `models.py` | Standard result representation |
| `aliases.py` | Artist aliases |
| `title_variants.py` | Title normalization and variants |
| `lyrics_ovh.py` | lyrics.ovh communication |
| `lyricsweb.py` | LyricsWeb communication and extraction |
| `lyrics_com.py` | Lyrics.com communication and extraction |
| `lrclib.py` | LRCLIB API communication and extraction |
| `metadata.py` | MP3/FLAC metadata and existing lyrics reading |
| `writer.py` | Safe MP3/FLAC lyrics writing and backup protection |
| `fetch_lyrics.py` | Command-line/application entry point |

This separation makes the project easier to test, maintain and extend.

---

# Search Flow

A typical search follows this sequence:

```text
Artist + Title
      │
      ▼
get_artist_aliases()
      │
      ▼
Artist candidates
      │
      ▼
generate_title_variants()
      │
      ▼
Title candidates
      │
      ▼
Search providers
(lyrics.ovh, LyricsWeb, Lyrics.com, LRCLIB)
      │
      ├── FOUND ───────────────► LyricsResult
      │
      └── NOT_FOUND
               │
               ▼
       Retry handling
       (when applicable)
               │
               ▼
          LyricsResult
```

The engine keeps the original artist and title from the audio file as the identity of the requested song, even when an alternative artist or title is used for the external search.

---


# Write Flow

Searching and writing are separate operations.

A typical audio-file workflow is:

```text
MP3 or FLAC
     │
     ▼
get_metadata()
     │
     ▼
Artist + Title
     │
     ▼
search_lyrics()
     │
     ▼
LyricsResult
     │
     ├── FOUND
     │     │
     │     ▼
     │   write_lyrics()
     │     │
     │     ├── Lyrics already exist?
     │     │      │
     │     │      ├── Yes + overwrite=False
     │     │      │        └── ALREADY_EXISTS
     │     │      │
     │     │      └── No, or overwrite=True
     │     │
     │     ▼
     │   create_backup()
     │     │
     │     ▼
     │   Write lyrics
     │     │
     │     ├── MP3: ID3 USLT frame
     │     │
     │     └── FLAC: LYRICS Vorbis comment
     │     │
     │     ▼
     │   WRITTEN
     │
     └── NOT_FOUND / ERROR
```

This design prevents a failed lyrics search from modifying the audio file. Existing lyrics are protected unless overwriting is explicitly enabled. Before a file is modified, the writer creates a backup.

---


# Provider Independence

Providers are isolated from the core engine.

A future provider can be added under:

```text
src/lyrics_engine/providers/
```

without moving search logic into the provider itself.

A provider should:

- Accept artist and title.
- Perform its own external request.
- Handle network failures.
- Handle unexpected responses.
- Return a `LyricsResult`.
- Avoid modifying audio files.
- Be independently testable.

The engine decides when and how providers are used.

---

# Testing Architecture

The project uses automated tests to verify individual components and complete behaviors.

Tests cover areas including:

- Result model behavior
- MP3 and FLAC metadata extraction
- Existing lyrics detection
- Title variants
- Artist aliases
- Lyrics writing for supported audio formats
- Existing lyrics protection
- MP3 and FLAC file handling
- Lyrics audit behavior

External providers should be tested without depending unnecessarily on live websites. Network behavior can be isolated or mocked so that provider tests remain predictable.

The project has also been tested against a real collection of MP3 files. FLAC writing and existing-lyrics protection have been tested separately using temporary files.

---


# Puddletag Integration

Puddletag integration is intentionally not part of the core engine.

The planned architecture is:

```text
┌───────────────────────────┐
│         Puddletag         │
│      plugin/interface     │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│      Lyrics Engine        │
│                           │
│      search_lyrics()      │
│      metadata             │
│      writer               │
└─────────────┬─────────────┘
              │
      ┌───────┼────────┬───────────┐
      ▼       ▼        ▼           ▼
 lyrics.ovh LyricsWeb Lyrics.com  LRCLIB
```

The Puddletag layer should provide application-specific user interface behavior while keeping the lyrics engine reusable outside Puddletag.

This prevents the core project from becoming tightly coupled to one music-tagging application.

---

# Design Principles

Lyrics Engine follows several important design principles.

## Separation of concerns

Searching, metadata reading, provider communication and audio-file writing are separate responsibilities.

## Safe modification

Audio files should not be modified unexpectedly.

Existing lyrics are protected by default and backups are created before modification.

## Provider independence

External lyrics services are isolated from the core search logic.

## Testability

Components should be independently testable wherever possible.

## Extensibility

New providers, aliases, title transformations and application integrations can be added without rewriting the entire engine.

## Application independence

The core engine does not depend on Puddletag and can be used by other applications or scripts.

---

# Future Architecture

Potential future improvements include:

- Additional lyrics providers
- A formal provider interface
- More extensive provider tests
- Provider configuration
- Improved error classification
- Configurable search order
- More robust HTML extraction
- More comprehensive CLI functionality
- Puddletag integration as a separate layer
- Additional metadata formats
- More detailed logging

These changes should preserve the separation between the core engine and application-specific integrations.
