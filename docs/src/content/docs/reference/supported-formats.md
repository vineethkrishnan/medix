---
title: Supported Formats
description: Every input format Medix recognises, every output it can produce.
---

## Input formats (20+)

Medix auto-discovers files with any of these extensions:

| Extension | Container / Codec family |
|-----------|--------------------------|
| `.vob` | DVD MPEG-2 Program Stream |
| `.mp4` | MPEG-4 Part 14 |
| `.mkv` | Matroska |
| `.avi` | Audio Video Interleave |
| `.mov` | QuickTime |
| `.wmv` | Windows Media Video |
| `.flv` | Flash Video |
| `.mpeg` / `.mpg` | MPEG-1/2 Program Stream |
| `.ts` | MPEG Transport Stream |
| `.webm` | WebM (Matroska subset) |
| `.m4v` | MPEG-4 Video |
| `.3gp` | 3GPP Mobile |
| `.ogv` | Ogg Video |
| `.mts` / `.m2ts` | AVCHD Blu-ray |
| `.divx` | DivX |
| `.asf` | Advanced Systems Format |
| `.rm` / `.rmvb` | RealMedia |
| `.f4v` | Flash Video (H.264) |

Extension matching is case-insensitive.

## Output formats

| Format | Extension | Default video | Default audio |
|--------|-----------|---------------|---------------|
| MP4 | `.mp4` | H.264 | AAC |
| MKV | `.mkv` | H.264 | AAC |
| WebM | `.webm` | VP9 | Opus |
| MOV | `.mov` | H.264 | AAC |
| AVI | `.avi` | H.264 | MP3 |
| TS | `.ts` | H.264 | AAC |

## Video codecs

| Codec | FFmpeg name |
|-------|-------------|
| H.264 | `libx264` |
| H.265 | `libx265` |
| VP9 | `libvpx-vp9` |
| AV1 | `libaom-av1` |
| MPEG-4 | `mpeg4` |
| Copy | `copy` (no re-encode) |

## Audio codecs

| Codec | FFmpeg name |
|-------|-------------|
| AAC | `aac` |
| MP3 | `libmp3lame` |
| Opus | `libopus` |
| AC3 | `ac3` |
| FLAC | `flac` |
| Copy | `copy` (no re-encode) |

## Resolutions

Original · 4K (3840×2160) · 2K (2560×1440) · 1080p · 720p · 480p · 360p

## Frame rates

Original · 24 · 25 · 30 · 48 · 60 fps

## Encoding presets

ultrafast · superfast · veryfast · faster · fast · **medium** · slow · slower · veryslow

## CRF range

`0` (lossless) — `23` (default) — `51` (worst).

## Audio bitrates

Auto · 96k · 128k · 192k · 256k · 320k
