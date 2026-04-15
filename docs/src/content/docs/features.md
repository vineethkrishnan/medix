---
title: Features
description: What Medix gives you out of the box.
---

## Interactive workflow

Medix walks you through conversion via a series of styled prompts:

1. **Discovery** — scans the path and shows a clean table of files with
   resolution, duration, and size.
2. **Source filter** — if multiple input formats exist, pick which ones to
   convert (multi-select checkbox).
3. **Output format** — choose from MP4, MKV, WebM, MOV, AVI, or TS.
4. **Advanced settings** — optionally tune video codec, audio codec,
   resolution, frame rate, CRF, preset, and audio bitrate.
5. **Confirmation** — review the conversion plan before anything runs.
6. **Progress** — per-file and overall progress bars with live ETA.
7. **Summary** — success/failure counts and error details.

## Batch conversion

- Convert a single file, a directory, or a directory tree (`-r`).
- Output directory defaults to `<input>/converted/` or can be set with `-o`.
- Filename collisions are handled automatically with an incrementing suffix.

## Dry-run preview

Preview everything without writing files using `--dry-run` (or `-n`). Medix
shows:

- The discovered files and their output paths
- A representative `ffmpeg` command that would be executed
- The complete conversion plan

## FFmpeg auto-install

If FFmpeg or `ffprobe` are missing, Medix detects your OS and package manager
and offers to install them for you. Supported managers:

- **macOS** — Homebrew, MacPorts
- **Linux** — APT, DNF, YUM, Pacman
- **Windows** — winget, Chocolatey, Scoop

## Format & codec support

| Category | Options |
|----------|---------|
| **Output formats** | MP4, MKV, WebM, MOV, AVI, TS |
| **Video codecs** | H.264, H.265, VP9, AV1, MPEG-4, copy |
| **Audio codecs** | AAC, MP3, Opus, AC3, FLAC, copy |
| **Resolutions** | Original, 4K, 2K, 1080p, 720p, 480p, 360p |
| **Frame rates** | Original, 24, 25, 30, 48, 60 fps |
| **Presets** | ultrafast → veryslow |
| **CRF range** | 0–51 (lower = higher quality) |
| **Audio bitrate** | Auto, 96k, 128k, 192k, 256k, 320k |

See [Supported Formats](/reference/supported-formats/) for the full input
list and default codec mappings.

## Cross-platform

Tested on CI across Python 3.9–3.13 on Ubuntu, macOS, and Windows.
