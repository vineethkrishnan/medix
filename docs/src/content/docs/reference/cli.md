---
title: CLI Reference
description: Complete reference for every Medix command, option, and argument.
---

## `medix`

The only command. Convert one file or a whole directory of media files.

### Synopsis

```
medix [OPTIONS] PATH
```

### Argument

| Argument | Description |
|----------|-------------|
| `PATH` | A single media file or a directory. Required. |

### Options

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `--output` | `-o` | path | `<input>/converted/` | Output directory. Created if it doesn't exist. |
| `--recursive` | `-r` | flag | `false` | Recurse into subdirectories when `PATH` is a directory. |
| `--dry-run` | `-n` | flag | `false` | Show the conversion plan and sample ffmpeg command without writing files. |
| `--version` | | flag | — | Print Medix version and exit. |
| `--help` | `-h` | flag | — | Print help and exit. |

### Examples

```bash
medix video.mp4
medix ~/Videos/
medix ~/Videos/ -r
medix ~/Videos/ -o ~/Converted/
medix ~/Videos/ --dry-run
medix ~/Videos/ -r -o ~/Converted/ -n
medix --version
```

## Module invocation

Medix can also be invoked as a Python module:

```bash
python -m medix [OPTIONS] PATH
```

Functionally identical to `medix`.

## Interactive prompts

When not in `--help` / `--version` mode, Medix shows a series of prompts:

| Prompt | Shown when |
|--------|-----------|
| Install FFmpeg? | FFmpeg / ffprobe not found |
| Which source formats? | Multiple input formats discovered |
| Which output format? | Always |
| Configure advanced settings? | Always |
| (advanced) Video codec | "Yes" to advanced |
| (advanced) Audio codec | "Yes" to advanced |
| (advanced) Resolution | "Yes" to advanced |
| (advanced) Frame rate | "Yes" to advanced |
| (advanced) Preset | "Yes" to advanced + H.264/H.265 codec |
| (advanced) CRF | "Yes" to advanced + H.264/H.265 codec |
| (advanced) Audio bitrate | "Yes" to advanced |
| Confirm plan | Always |

## Defaults by output format

| Format | Video | Audio |
|--------|-------|-------|
| MP4 | H.264 (libx264) | AAC |
| MKV | H.264 (libx264) | AAC |
| WebM | VP9 (libvpx-vp9) | Opus |
| MOV | H.264 (libx264) | AAC |
| AVI | H.264 (libx264) | MP3 |
| TS | H.264 (libx264) | AAC |

Every default can be overridden via advanced settings.
