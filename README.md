# Medix

[![CI](https://github.com/vineethkrishnan/medix/actions/workflows/ci.yml/badge.svg)](https://github.com/vineethkrishnan/medix/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-medix.vineethnk.in-8b5cf6)](https://medix.vineethnk.in)
[![PyPI](https://img.shields.io/pypi/v/medix)](https://pypi.org/project/medix/)
[![Python](https://img.shields.io/pypi/pyversions/medix)](https://pypi.org/project/medix/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A fancy command-line media format converter powered by FFmpeg. Interactively choose source and target formats, tweak advanced encoding settings, and watch conversions fly with real-time progress bars.

<p align="center">
  <img src="assets/demo-banner.svg" width="700" alt="medix banner" />
</p>

> **📖 Full documentation:** [medix.vineethnk.in](https://medix.vineethnk.in) — installation, guides, CLI reference, and [roadmap](https://medix.vineethnk.in/roadmap/).

---

## Demo

### File Discovery

Medix scans your path and presents a clean table of all discovered media files with resolution, duration, and size.

<p align="center">
  <img src="assets/demo-files.svg" width="700" alt="discovered files table" />
</p>

### Conversion Plan & Progress

Review your settings before starting, then watch per-file and overall progress in real time.

<p align="center">
  <img src="assets/demo-settings.svg" width="700" alt="conversion plan" />
</p>

<p align="center">
  <img src="assets/demo-progress.svg" width="700" alt="conversion progress" />
</p>

### Auto-Install Prerequisites

No FFmpeg? No problem. Medix detects your OS, finds a package manager, and offers to install it for you.

<p align="center">
  <img src="assets/demo-prereq.svg" width="700" alt="auto-install prerequisites" />
</p>

### Completion Summary

<p align="center">
  <img src="assets/demo-complete.svg" width="700" alt="conversion complete" />
</p>

---

## Requirements

| Dependency | Minimum Version | Check Command |
|-----------|----------------|---------------|
| **Python** | 3.9+ | `python3 --version` |
| **FFmpeg** | 4.4+ | `ffmpeg -version` |
| **ffprobe** | (bundled with FFmpeg) | `ffprobe -version` |

> **Note:** If FFmpeg is not installed, Medix will detect your system and offer to install it automatically via your package manager (Homebrew, APT, DNF, Pacman, winget, Chocolatey, and more).

### Supported Platforms

- macOS 12+ (Homebrew, MacPorts)
- Ubuntu 20.04+ / Debian 11+ (APT)
- Fedora / RHEL (DNF, YUM)
- Arch Linux (Pacman)
- Windows 10+ (winget, Chocolatey, Scoop)

---

## Installation

Medix is on [PyPI](https://pypi.org/project/medix/) and mirrored on [libraries.io](https://libraries.io/pypi/medix). Pick whichever workflow fits you best — the [full installation guide](https://medix.vineethnk.in/getting-started/installation/) covers every option.

### From PyPI (recommended)

```bash
pip install medix
```

### With pipx (isolated global install)

```bash
pipx install medix
```

### From source

```bash
git clone https://github.com/vineethkrishnan/medix.git
cd medix
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

### From a Git tag or branch directly

```bash
pip install "git+https://github.com/vineethkrishnan/medix.git@main"
```

### As a dependency in `pyproject.toml`

```toml
[project]
dependencies = ["medix>=1.3.0"]
```

### Verify

```bash
medix --version
```

### FFmpeg

Medix needs FFmpeg at runtime, but you don't have to install it first — on first run it detects your platform and offers to install it via Homebrew, APT, DNF, Pacman, winget, Chocolatey, or Scoop. See the [FFmpeg Auto-Install guide](https://medix.vineethnk.in/guides/ffmpeg-setup/) for manual install commands.

---

## Usage

```bash
# Convert a single file
medix /path/to/video.vob

# Convert all media files in a directory
medix /path/to/videos/

# Recurse into subdirectories
medix /path/to/videos/ -r

# Specify output directory
medix /path/to/videos/ -o /path/to/output/

# Dry run — see what would happen without converting
medix /path/to/videos/ --dry-run
```

### What Happens

1. Medix checks for FFmpeg — if missing, it offers to install it automatically.
2. Scans the path and lists discovered media files with metadata (resolution, duration, size).
3. If multiple source formats exist, you pick which ones to convert.
4. Choose an output format (MP4, MKV, WebM, MOV, AVI, TS).
5. Optionally configure advanced settings — codec, resolution, frame rate, CRF, preset, bitrate.
6. Review the conversion plan and confirm.
7. Watch per-file and overall progress bars in real time.

### Dry Run

Use `--dry-run` (or `-n`) to preview the conversion plan without writing any files. Medix will show you the file mapping and the exact ffmpeg command that would be executed:

```bash
medix /path/to/videos/ --dry-run
```

### CLI Reference

```
Usage: medix [OPTIONS] PATH

  Medix - Convert media files between formats with style.

Options:
  -o, --output PATH  Output directory (default: <input>/converted/)
  -r, --recursive    Recurse into subdirectories
  -n, --dry-run      Show what would be done without converting
  --version          Show version and exit
  -h, --help         Show help and exit
```

---

## Supported Formats

### Input (20+)

VOB, MP4, MKV, AVI, MOV, WMV, FLV, MPEG, MPG, TS, WebM, M4V, 3GP, OGV, MTS, M2TS, DIVX, ASF, RM, RMVB, F4V

### Output

| Format | Default Codecs | Best For |
|--------|---------------|----------|
| **MP4** | H.264 + AAC | Universal playback |
| **MKV** | H.264 + AAC | Flexible container |
| **WebM** | VP9 + Opus | Web streaming |
| **MOV** | H.264 + AAC | Apple ecosystem |
| **AVI** | H.264 + MP3 | Legacy compatibility |
| **TS** | H.264 + AAC | Broadcast / streaming |

### Advanced Settings

When enabled, you can configure:

- **Video codec** — H.264, H.265, VP9, AV1, MPEG-4, or copy (no re-encode)
- **Audio codec** — AAC, MP3, Opus, AC3, FLAC, or copy
- **Resolution** — Keep original, 4K, 2K, 1080p, 720p, 480p, 360p
- **Frame rate** — Keep original, 24, 25, 30, 48, 60 fps
- **Encoding preset** — ultrafast to veryslow (H.264/H.265)
- **CRF quality** — 0–51 (lower = better quality, larger file)
- **Audio bitrate** — Auto, 96k–320k

---

## Development

```bash
git clone https://github.com/vineethkrishnan/medix.git
cd medix
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run the full test suite
pytest

# With coverage report
pytest --cov=medix --cov-report=term-missing

# Run a specific test file
pytest tests/test_converter.py
```

Tests cover all modules (converter, CLI, dependencies, formats) and run on every push across Python 3.9–3.13 on Linux, macOS, and Windows via CI.

### Re-generate demo screenshots

```bash
python assets/generate_demos.py
```

This project uses [Conventional Commits](https://www.conventionalcommits.org/) and [Release Please](https://github.com/googleapis/release-please) for automated versioning and changelog generation.

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines and the [Release Process docs](https://medix.vineethnk.in/development/releases/) for how releases are cut.

---

## Documentation

The full documentation site is at **[medix.vineethnk.in](https://medix.vineethnk.in)** — built with [Astro Starlight](https://starlight.astro.build/), searchable via Pagefind, and deployed to Cloudflare Pages.

| Section | What's there |
|---------|--------------|
| [Getting Started](https://medix.vineethnk.in/getting-started/installation/) | Requirements, installation, quick start |
| [Guides](https://medix.vineethnk.in/guides/cli-usage/) | CLI usage, dry-run, formats, advanced settings, FFmpeg setup |
| [Reference](https://medix.vineethnk.in/reference/cli/) | Complete CLI reference and supported formats matrix |
| [Development](https://medix.vineethnk.in/development/contributing/) | Contributing, testing, release process |
| [Roadmap](https://medix.vineethnk.in/roadmap/) | What's coming in v1.4, v1.5, v1.6, and v2.0 |

To preview the docs locally:

```bash
cd docs
npm install
npm run dev
```

---

## Roadmap

Highlights from the [full roadmap](https://medix.vineethnk.in/roadmap/):

- **v1.4** — named presets, `.medixrc` config file, non-interactive mode, JSON output, shell completion
- **v1.5** — metadata/subtitle preservation, hardware acceleration (VideoToolbox / NVENC / QuickSync / VAAPI), two-pass encoding, HDR tone-mapping, thumbnails
- **v1.6** — resume support, parallel encoding, watch mode, smart skip
- **v2.0** — stable Python API, plugin system, TUI mode

Vote on items or suggest new ones on the [issue tracker](https://github.com/vineethkrishnan/medix/issues).

---

## License

[MIT](LICENSE) — see [LICENSE](LICENSE) for details.
