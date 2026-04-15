---
title: Contributing
description: How to set up a dev environment and contribute to Medix.
---

Thanks for considering a contribution to Medix! The short version:

1. Fork and clone
2. `pip install -e ".[dev]"`
3. Make your change
4. Run `pytest` and `ruff check .` locally
5. Commit with a [Conventional Commits](https://www.conventionalcommits.org/)
   message
6. Open a PR

## Dev setup

```bash
git clone https://github.com/vineethkrishnan/medix.git
cd medix

python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -e ".[dev]"
```

This installs Medix in editable mode plus the test and lint tooling
(`pytest`, `pytest-cov`, `ruff`).

## Project layout

```
medix/
├── medix/
│   ├── cli.py          # Click CLI, interactive prompts, Rich UI
│   ├── converter.py    # FFmpeg wrapper, command building, conversion
│   ├── dependencies.py # FFmpeg detection & auto-install
│   └── formats.py      # Format/codec/preset/bitrate constants
├── tests/              # 119+ unit tests
├── docs/               # This Astro documentation site
└── .github/workflows/  # CI + release-please + docs deploy
```

## Code style

- **Ruff** handles both linting and formatting.
- Run `ruff check .` and `ruff format .` before pushing.
- Follow the existing module layout — UI in `cli.py`, ffmpeg logic in
  `converter.py`, dependency detection in `dependencies.py`.

## Commit style

Medix uses [Conventional Commits](https://www.conventionalcommits.org/)
with [Release Please](https://github.com/googleapis/release-please) for
automated releases. Your commit prefix determines the release bump:

| Prefix | Effect |
|--------|--------|
| `feat:` | minor bump |
| `fix:` | patch bump |
| `feat!:` or `BREAKING CHANGE:` | major bump |
| `chore:`, `docs:`, `refactor:`, `test:`, `ci:`, `style:` | no bump |

## Running tests

```bash
# Full suite
pytest

# With coverage
pytest --cov=medix --cov-report=term-missing

# A specific file
pytest tests/test_converter.py

# A specific test
pytest tests/test_converter.py::TestBuildCommand::test_video_codec_h264
```

See [Testing](/development/testing/) for deeper details.

## Docs

The docs in `docs/` are built with [Astro Starlight](https://starlight.astro.build/)
and deployed to Cloudflare Pages on every merge to `main` that touches
`docs/`. To preview locally:

```bash
cd docs
npm install
npm run dev
```

Then open http://localhost:4321.

## Reporting bugs

Open an [issue on GitHub](https://github.com/vineethkrishnan/medix/issues)
and include:

- Your OS and Python version
- `medix --version`
- `ffmpeg -version`
- Exact command and full error output
