# Contributing to Lyrics Engine

Thank you for your interest in contributing to Lyrics Engine.

The project is designed to be modular, testable and independent from any
specific music application. Contributions are welcome, especially those
that improve reliability, provider support, testing and documentation.

## Development environment

Lyrics Engine currently targets Python 3.12 or newer.

Create or activate a virtual environment and install the project in editable
mode:

```bash
python -m pip install -e .
```

Editable installation allows changes made inside `src/lyrics_engine/` to be 
used immediately during development.

## Running the tests

Before submitting changes, run the complete test suite:

```
python -m unittest discover -s tests -v
```

All existing tests should pass before a contribution is submitted.

## Development workflow

A typical workflow is:

1. Create a branch for the change.
2. Make the changes.
3. Add or update tests where appropriate.
4. Run the complete test suite.
5. Review the changes with Git.
6. Commit the changes with a clear message.
7. Open a pull request.

Example:

```
git checkout -b feature/my-change
```

Keep commits focused on one logical change whenever possible.

## Adding a lyrics provider

Lyrics providers should be implemented as independent modules under:

```
src/lyrics_engine/providers/
```

A provider should not contain logic that belongs to the core search engine.

Provider implementations should:

-  use reasonable network timeouts;
-  handle connection failures;
-  handle unexpected HTTP responses;
-  avoid crashing the main search process;
-  return a `LyricsResult`;
-  provide a clear provider name;
-  be independently testable.

The core engine should remain responsible for provider orchestration and
fallback behavior.

## Testing providers

Provider behavior should be covered by automated tests whenever practical.

Tests should avoid depending on a live external website when possible.
Network behavior should preferably be isolated or mocked so that the test 
suite remains deterministic.

## Lyrics and copyright

Do not commit complete copyrighted song lyrics to the repository.

Tests should use short, legally appropriate fixtures or synthetic text
rather than reproducing full copyrighted lyrics.

Provider attribution and licensing requirements must be respected.

## Safe file modification

Changes involving MP3 metadata must preserve the project's safety
principles.

In particular:

- Do not silently overwrite existing lyrics.
- Preserve the existing overwrite protection.
- Create backups before modifying files.
- Avoid destructive behavior without explicit user intent.
- Add tests for any change affecting metadata writing.

## Code style

Prefer:

- small focused functions;
- clear names;
- explicit behavior;
- minimal duplication;
- standard Python libraries where practical;
- comments explaining why something is necessary rather than what obvious
    code is doing.

Avoid unnecessary architectural complexity.

## Documentation

Changes that introduce user-visible behavior should update the relevant
documentation.

Keep the README accurate. Do not document planned functionality as if it
were already implemented.

## Puddletag integration

Puddletag integration is a planned direction for the project.

The core lyrics engine should remain independent from Puddletag. Integration
code should be kept in a separate layer so that the engine can also be used 
by other applications.

## Reporting bugs

When reporting a bug, include as much useful information as possible:

- Python version;
- operating system;
- Lyrics Engine version or Git commit;
- relevant command or operation;
- expected behavior;
- actual behavior;
- error message or traceback, if available.

Do not include private credentials, API keys or personal information.

## Feature requests

Feature requests are welcome.

Please describe:

- the problem being solved;
- the proposed behavior;
- why the change belongs in the core engine;
- whether the change could affect existing behavior.

## Pull requests

Before submitting a pull request, verify that:

- the test suite passes;
- new functionality has appropriate tests;
- documentation is updated when necessary;
- no copyrighted lyric content has been added;
- no credentials or private information are included;
- the changes are focused and understandable.

## License

Lyrics Engine is released under the MIT License.

By contributing, you agree that your contribution may be distributed under 
the project's license.

See the `LICENSE` file for the complete license text.

## Development assistance

This project is developed with assistance from OpenAI's ChatGPT
(GPT-5.6 Luna), used for software architecture, refactoring, testing, 
documentation and development guidance.

Human contributors remain responsible for reviewing and validating the code 
and documentation they submit.
