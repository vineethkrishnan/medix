---
title: Testing
description: The Medix test suite — structure, conventions, and how to run it.
---

Medix ships with a comprehensive test suite: **119+ unit tests** covering
all four modules, running on Python 3.9–3.13 across Ubuntu, macOS, and
Windows in CI.

## Running tests

```bash
# Full suite
pytest

# With coverage report
pytest --cov=medix --cov-report=term-missing

# Single file
pytest tests/test_converter.py

# Single test
pytest tests/test_converter.py::TestBuildCommand::test_video_codec_h264

# Show stdout during tests
pytest -s
```

The `pyproject.toml` sets sensible defaults:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short"
```

## Test layout

| File | Covers | Highlights |
|------|--------|-----------|
| `tests/test_formats.py` | `medix/formats.py` | Format / codec / preset constants |
| `tests/test_cli.py` | `medix/cli.py` | Discovery, prompts, output resolution |
| `tests/test_converter.py` | `medix/converter.py` | Command building, probing, conversion |
| `tests/test_dependencies.py` | `medix/dependencies.py` | FFmpeg detection, package manager detection |

## What we test

- **Pure logic** — command building, path resolution, format filtering
- **Integration boundaries** — ffprobe parsing, subprocess calls (mocked)
- **Cross-platform behaviour** — package manager detection on macOS / Linux
  / Windows via mocked `platform` calls
- **Edge cases** — filename collisions, negative durations, missing codecs,
  empty directories

## What we don't test

- **Actual FFmpeg execution.** All subprocess calls are mocked — CI runs
  without FFmpeg installed.
- **Library plumbing.** Thin wrappers over click/rich/questionary are not
  worth testing.

## CI matrix

On every push and PR, GitHub Actions runs:

- **Lint** — Python 3.12 + ruff check + ruff format check
- **Tests** — Python 3.9, 3.10, 3.11, 3.12, 3.13 × Ubuntu / macOS / Windows

That's 15 test jobs per push. See `.github/workflows/ci.yml`.

## Adding a test

Follow the existing pattern in the file for the module you're touching:

```python
class TestBuildCommand:
    def test_video_codec_h264(self):
        settings = ConvertSettings(video_codec="H.264")
        command = build_command("in.mp4", "out.mp4", settings)
        assert "libx264" in command
```

Prefer parametrisation for multiple input values:

```python
@pytest.mark.parametrize("codec,expected", [
    ("H.264", "libx264"),
    ("H.265", "libx265"),
    ("VP9", "libvpx-vp9"),
])
def test_codec_mapping(codec, expected):
    ...
```
