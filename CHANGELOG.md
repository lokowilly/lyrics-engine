# Changelog

All notable changes to Lyrics Engine will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Modular lyrics engine architecture.
- `LyricsResult` model for standardized provider results.
- Independent lyrics provider modules.
- `lyrics.ovh` provider.
- `LyricsWeb` provider.
- Artist and title alias support.
- Title variant generation for lyrics searches.
- MP3 metadata reading.
- USLT lyrics reading and writing.
- Protection against overwriting existing lyrics.
- Automatic `.bak` backups before MP3 modification.
- Dry-run mode for lyrics processing.
- Lyrics audit functionality.
- Automated test suite.
- Python packaging through `pyproject.toml`.
- Editable installation support.
- Contribution guidelines.

### Changed

- Refactored the lyrics engine into independent modules.
- Separated metadata handling from the core lyrics engine.
- Separated the `LyricsResult` model from the engine implementation.
- Improved lyrics search reliability through aliases and title variants.
- Structured lyrics providers independently from the core engine.

### Fixed

- Improved handling of titles containing punctuation, apostrophes and
  parentheses.
- Prevented existing USLT lyrics from being silently overwritten.
- Improved safety of MP3 metadata modifications.

### Testing

- Automated test suite currently contains 14 tests.
- Tested against a real collection of 18 MP3 files.
- Verified USLT writing and existing-lyrics protection.
- Verified metadata reading from real MP3 files.
- Verified title variants and aliases.
- Verified lyrics audit results for 18 files with USLT frames.
- Verified that no duplicate USLT frames were created.

### Documentation

- Added project README.
- Added MIT license.
- Added contribution guidelines.

## Future

Planned areas of development include:

- Additional lyrics providers.
- More comprehensive provider tests.
- Provider attribution and licensing documentation.
- Architecture documentation.
- Puddletag integration.
- A dedicated Puddletag plugin layer independent from the core engine.
- Improved CLI documentation and user workflows.


[Keep a Changelog]: https://keepachangelog.com/en/1.1.0/
[Semantic Versioning]: https://semver.org/
