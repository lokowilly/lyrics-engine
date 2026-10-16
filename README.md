# Lyrics Engine

Extensible Python lyrics engine for music metadata applications.

Lyrics Engine searches for song lyrics using multiple providers, applies
controlled artist aliases and title variants, and can write the result into MP3 ID3 `USLT` frames or FLAC
Vorbis `LYRICS` comments.

The project is designed as an independent library so it can later be used
by applications such as metadata editors, music managers and Puddletag
extensions.

## Current status

This project is currently under active development.

The core lyrics engine supports MP3 and FLAC files.

Collection inventory:

- 477 MP3 files
- 341 FLAC files
- 818 audio files in total

These figures describe the current collection inventory, not the number of
files processed by Lyrics Engine.

Historical MP3 validation:

- 18 MP3 files audited
- 18 files containing lyrics
- 18 valid `USLT` frames
- 0 duplicate lyric frames
- 0 files without lyrics

Current project validation:

- 42 automated tests passed in the latest full test run
- FLAC writing and existing-lyrics protection tested on temporary copies
- Backup protection before lyric modification
- Dry-run mode available

## Features

- Multiple lyrics providers
- Provider fallback
- Artist aliases
- Song title variants
- Unicode normalization
- Existing lyrics detection
- Protection against accidental overwriting
- Automatic `.bak` backup before modification
- MP3 ID3 `USLT` writing
- FLAC Vorbis `LYRICS` writing
- MP3 and FLAC metadata reading
- Dry-run mode
- Python package structure
- Automated tests

## Project structure

```text
music/
├── fetch_lyrics.py
├── pyproject.toml
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
```

## Installation

The project currently targets Python 3.12 or newer.

Clone the repository and create or activate a Python virtual environment.

Then install the project in editable mode:

```bash
python -m pip install -e .
```

Editable installation is useful during development because changes made
inside `src/lyrics_engine/` are immediately available to Python.

## Running tests

From the project root:

```bash
python -m unittest discover -s tests -v
```

## Fetching lyrics

The command-line frontend is:

```bash
python fetch_lyrics.py
```

For a safe preview without modifying files:

```bash
python fetch_lyrics.py --dry-run "/path/to/music"
```

The dry-run mode does not modify audio files.

## Safety

Lyrics Engine is designed to avoid accidental data loss.

By default, existing lyrics are not overwritten.

Before writing new lyrics to an MP3 or FLAC file, the application
creates a `.bak` backup when one does not already exist.

Overwriting existing lyrics requires the explicit `--overwrite` option.

## Providers

The current engine uses:

- lyrics.ovh
- LyricsWeb
- Lyrics.com
- LRCLIB

Provider-specific code is isolated under:

```text
src/lyrics_engine/providers/
```

This allows additional providers to be added without rewriting the core
search engine.

Provider availability and website behavior may change over time.

## Development philosophy

The project favors:

- Small independent modules
- Explicit behavior
- Safe file modification
- Automated testing
- Provider isolation
- Reproducible development environments
- Open-source collaboration

The lyrics engine should remain independent from any particular graphical
application.

## Future direction

Possible future work includes:

- Additional lyrics providers
- More comprehensive provider tests
- Better search diagnostics
- Configuration of providers
- Puddletag integration
- Plugin/API layer
- Improved command-line interface
- Packaging and distribution

These features are planned ideas and are not necessarily implemented yet.

## License

This project is licensed under the MIT License. See LICENSE for details.

The MIT license applies to this project's code, not to third-party lyrics or provider services. Each provider may have its own terms, attribution requirements, and usage restrictions.

## Development assistance

This project was developed with assistance from OpenAI's ChatGPT
(GPT-5.6 Luna), used for software architecture, refactoring, testing,
documentation, and development guidance.

## Project status

This is an experimental development project.

Interfaces and internal APIs may change while the architecture is being
developed.

---

## The Script Yogi

```text
                 .-""""-.
              .-'  _  _  '-.
             /    (o)(o)    \
            |       __       |
            |    .-'  '-.    |
             \  /  .--.  \  /
              '.  \____/  .'
                '-.____.-'
                   /||\
              ____/ || \____
             /     /  \     \
            /_____/    \_____\
                 YOGANANDA
                DEL SCRIPT
```

> “First make it work. Then make it beautiful.
> And always keep a backup.”

*— The Script Yogi*
