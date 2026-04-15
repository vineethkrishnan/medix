---
title: Quick Start
description: Convert your first media file with Medix in under a minute.
---

This walks through a typical first run. Swap the paths for your own.

## 1. Install

```bash
pip install medix
```

## 2. Point Medix at a file

```bash
medix /path/to/video.vob
```

Or a whole directory:

```bash
medix /path/to/videos/
```

## 3. Let Medix check FFmpeg

If FFmpeg is missing, Medix will offer to install it for you. Accept, and it
runs the right `brew` / `apt` / `winget` command under the hood.

## 4. Pick an output format

Medix lists discovered files, then asks which output format you want:

```
? Choose output format
  MP4 (H.264 + AAC — universal playback)
  MKV (H.264 + AAC — flexible container)
  WebM (VP9 + Opus — web streaming)
  MOV (H.264 + AAC — Apple ecosystem)
  AVI (H.264 + MP3 — legacy)
  TS (H.264 + AAC — broadcast)
```

## 5. (Optional) Tweak encoding

Say yes to advanced settings if you want to override the defaults — video
codec, resolution, frame rate, CRF, preset, audio bitrate.

## 6. Confirm and watch it run

Medix shows the conversion plan, you confirm, and the progress bars take
over.

## Common invocations

```bash
# Single file
medix video.mp4

# Directory
medix ~/Videos/

# Recurse into subdirectories
medix ~/Videos/ -r

# Custom output directory
medix ~/Videos/ -o ~/Converted/

# Preview without converting
medix ~/Videos/ --dry-run

# Recurse + dry run + custom output
medix ~/Videos/ -r -o ~/Converted/ --dry-run
```

## Next steps

- [CLI Usage](/guides/cli-usage/) — all flags explained
- [Dry Run Mode](/guides/dry-run/) — safety-first workflow
- [Advanced Settings](/guides/advanced-settings/) — codec tuning
