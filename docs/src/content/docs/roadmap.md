---
title: Roadmap
description: What's planned for upcoming Medix releases.
---

:::note
This roadmap is directional, not a commitment. Priorities may shift based on
feedback and real-world usage. Got an idea?
[Open an issue](https://github.com/vineethkrishnan/medix/issues/new) or
start a discussion.
:::

## Current release — v1.3.x

Shipped in `v1.3.0`:

- `--dry-run` / `-n` to preview conversions without touching disk
- Full 119-test unit suite across all modules
- Cross-platform CI (Python 3.9–3.13 × Ubuntu / macOS / Windows)
- Published to PyPI and mirrored on libraries.io
- Astro Starlight documentation site on Cloudflare Pages

## v1.4 — Config & profiles

**Target: Q2 2026**

- [ ] **Named presets** — save a set of advanced settings as a profile
      (`medix --preset web-optimized`)
- [ ] **`.medixrc` / `medix.toml`** — project-level defaults so teams can
      commit conversion settings to a repo
- [ ] **Non-interactive mode** — `--yes` / `--format mp4 --crf 22` for
      scripting and CI pipelines
- [ ] **JSON output mode** — `--json` for the dry-run plan and final
      summary, so wrapper tools can parse results
- [ ] **Shell completion** — tab completion for bash, zsh, fish, and
      PowerShell

## v1.5 — Quality & metadata

**Target: Q3 2026**

- [ ] **Metadata preservation** — copy tags, chapter markers, and subtitle
      tracks by default
- [ ] **Subtitle handling** — `--subs copy | burn | extract | none`
- [ ] **Two-pass encoding** — opt-in for target-bitrate workflows
- [ ] **Hardware acceleration** — auto-detect and offer VideoToolbox (macOS),
      NVENC (NVIDIA), QuickSync (Intel), VAAPI (Linux)
- [ ] **HDR tone-mapping** — basic HDR → SDR conversion helper
- [ ] **Thumbnail extraction** — `--thumbnail` to emit poster frames

## v1.6 — Batch intelligence

**Target: Q4 2026**

- [ ] **Resume support** — continue a previously interrupted batch
- [ ] **Parallel encoding** — `--parallel N` with smart scheduling
- [ ] **Watch mode** — `medix --watch <dir>` auto-converts new files
- [ ] **Smart skip** — detect when an output is already newer than its input
      and skip

## v2.0 — Stable API & extensibility

**Target: H1 2027**

- [ ] **Stable Python API** — `from medix import Converter, Settings` for
      programmatic use
- [ ] **Plugin system** — register new output formats or codecs via entry
      points
- [ ] **Telemetry opt-in** — anonymous usage stats to guide future work
- [ ] **TUI mode** — full-screen interactive mode for long batch workflows

## Ideas backlog

Things being considered but not yet scheduled:

- Audio-only extraction (MP3, Opus, FLAC, WAV)
- GIF / animated WebP output
- Image sequence input (folder of PNGs → video)
- Trim / cut support without re-encoding
- Concatenation (`medix concat file1.mp4 file2.mp4 -o joined.mp4`)
- Remote source support (URLs, S3, GCS)
- A brew formula and scoop manifest
- A Homebrew tap for beta builds
- Docker image with FFmpeg pre-installed
- Integration with whisper.cpp for auto-subtitle generation

## Vote or propose

This roadmap is a living document. To influence it:

- 👍 an existing item in the [issues list](https://github.com/vineethkrishnan/medix/issues)
- Open a new issue with the `enhancement` label
- Start a [discussion](https://github.com/vineethkrishnan/medix/discussions)
  for larger ideas
