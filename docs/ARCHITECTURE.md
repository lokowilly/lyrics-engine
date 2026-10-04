# Lyrics Engine Architecture

## Overview

Lyrics Engine is designed as a modular Python library for searching, retrieving and safely storing song lyrics in MP3 files.

The core engine is independent from any specific music application. This allows the same functionality to be used from a command-line tool, a future Puddletag integration, or other applications.

The architecture separates:

- Search orchestration
- Result representation
- Artist aliases
- Title variants
- Lyrics providers
- MP3 metadata reading
- Lyrics writing and file protection

The main search flow is:

```text
MP3 metadata
     │
     ▼
   engine.py
     │
     ├── artist aliases
     │
     ├── title variants
     │
     ▼
 lyrics.ovh
     │
     ├── FOUND ───────────────► LyricsResult
     │
     └── NOT_FOUND
             │
             ▼
         LyricsWeb
             │
             ▼
        LyricsResult
```

---

## Project Structure

```text
lyrics-engine/
│
├── fetch_lyrics.py
├── pyproject.toml
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CHANGELOG.md
│
├── src/
│   └── lyrics_engine/
│       ├── __init__.py
│       ├── aliases.py
│       ├── engine.py
│       ├── metadata.py
│       ├── models.py
│       ├── title_variants.py
│       ├── writer.py
│       │
│       └── providers/
│           ├── __init__.py
│           ├── lyrics_ovh.py
│           └── lyricsweb.py
│
└── tests/
    └── ...
```

---

# Core Components

## `engine.py`

The engine is the main orchestration layer.

Its responsibility is to coordinate the search process without implementing provider-specific HTTP logic or MP3 modification.

The main function is:

```python
search_lyrics(artist, title)
```

The engine:

1. Receives the artist and title.
2. Obtains possible artist aliases.
3. Generates title variants.
4. Searches `lyrics.ovh`.
5. Returns the first valid result.
6. Uses LyricsWeb as a fallback when lyrics.ovh does not find the lyrics.
7. Returns a standardized `LyricsResult`.

The engine does not write to MP3 files.

This separation is intentional: searching for lyrics and modifying an MP3 are independent operations.

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

The title variant generator does not perform network requests and does not modify MP3 files.

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
- Modify MP3 files

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

The provider does not modify MP3 files.

---

# MP3 Metadata

## `metadata.py`

`metadata.py` is responsible for reading MP3 metadata.

It currently provides two main functions:

```python
get_metadata(mp3_path)
```

and:

```python
read_existing_lyrics(mp3_path)
```

### `get_metadata()`

Reads the ID3 artist and title frames:

```text
TPE1 → Artist
TIT2 → Title
```

The function does not modify the MP3.

It returns a `LyricsResult` containing the artist and title when successful.

If the required metadata cannot be read, an `ERROR` result is returned.

### `read_existing_lyrics()`

Reads existing ID3 `USLT` frames.

The function does not modify the MP3.

If the file cannot be read, it returns an empty list rather than modifying or damaging the file.

Keeping metadata reading separate from the search engine allows the engine to operate independently of a particular MP3-reading workflow.

---

# MP3 Lyrics Writing

## `writer.py`

`writer.py` contains the functionality that modifies MP3 files.

This module is deliberately separated from the search engine.

The main functions are:

```python
create_backup(mp3_path)
```

and:

```python
write_lyrics(...)
```

---

## Backup Protection

Before modifying an MP3, the writer creates a backup:

```text
filename.mp3.bak
```

An existing backup is not overwritten.

This provides a recovery point before changing the original file.

---

## Existing Lyrics Protection

Before writing, `write_lyrics()` checks for existing `USLT` frames.

By default:

```python
overwrite=False
```

If lyrics already exist, the function returns:

```text
ALREADY_EXISTS
```

and does not modify the MP3.

This prevents existing lyrics from being silently destroyed.

---

## Explicit Overwrite

When:

```python
overwrite=True
```

the existing `USLT` frames are removed before the new lyrics are written.

This makes overwriting an explicit operation rather than an accidental side effect.

---

## USLT Writing

Lyrics are stored in an ID3 `USLT` frame.

The current implementation uses:

```text
language = eng
description = Lyrics
encoding = 3
```

The file is saved using ID3 version 2.3.

The writer returns:

```text
WRITTEN
```

when the operation succeeds.

If an exception occurs, it returns:

```text
ERROR
```

with an explanatory message.

---

# Separation of Responsibilities

A key design principle of Lyrics Engine is that each component has one primary responsibility.

| Component | Responsibility |
|---|---|
| `engine.py` | Search orchestration |
| `models.py` | Standard result representation |
| `aliases.py` | Artist aliases |
| `title_variants.py` | Title normalization and variants |
| `lyrics_ovh.py` | lyrics.ovh communication |
| `lyricsweb.py` | LyricsWeb communication and extraction |
| `metadata.py` | MP3 metadata and USLT reading |
| `writer.py` | Safe MP3 modification |
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
lyrics.ovh
      │
      ├── FOUND ───────────────► LyricsResult
      │
      └── NOT_FOUND
               │
               ▼
          LyricsWeb
               │
               ▼
          LyricsResult
```

The engine keeps the original artist and title from the MP3 as the identity of the requested song, even when an alternative artist or title is used for the external search.

---

# Write Flow

Searching and writing are separate operations.

A typical MP3 workflow is:

```text
MP3
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
 │     ├── Existing USLT?
 │     │      │
 │     │      ├── Yes + overwrite=False
 │     │      │        └── ALREADY_EXISTS
 │     │      │
 │     │      └── No
 │     │
 │     ▼
 │   create_backup()
 │     │
 │     ▼
 │   Write USLT
 │     │
 │     ▼
 │   WRITTEN
 │
 └── NOT_FOUND / ERROR
```

This design prevents a failed lyrics search from modifying the MP3.

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
- Avoid modifying MP3 files.
- Be independently testable.

The engine decides when and how providers are used.

---

# Testing Architecture

The project uses automated tests to verify individual components and complete behaviors.

Tests cover areas including:

- Result model behavior
- Metadata extraction
- Existing USLT detection
- Title variants
- Artist aliases
- Lyrics writing
- Existing lyrics protection
- Real MP3 metadata
- Lyrics audit behavior

External providers should be tested without depending unnecessarily on live websites. Network behavior can be isolated or mocked so that provider tests remain predictable.

The project also has been tested against a real collection of MP3 files.

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
      ┌───────┼────────┐
      ▼       ▼        ▼
  lyrics.ovh LyricsWeb  future
```

The Puddletag layer should provide application-specific user interface behavior while keeping the lyrics engine reusable outside Puddletag.

This prevents the core project from becoming tightly coupled to one music-tagging application.

---

# Design Principles

Lyrics Engine follows several important design principles.

## Separation of concerns

Searching, metadata reading, provider communication and MP3 writing are separate responsibilities.

## Safe modification

MP3 files should not be modified unexpectedly.

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
