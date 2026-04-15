---
title: Formats & Codecs
description: Which input formats Medix understands and which outputs it produces.
---

## Input formats

Medix recognises 20+ common media containers as inputs:

VOB, MP4, MKV, AVI, MOV, WMV, FLV, MPEG, MPG, TS, WebM, M4V, 3GP, OGV,
MTS, M2TS, DIVX, ASF, RM, RMVB, F4V.

Files matching these extensions are auto-discovered when you point Medix at
a directory. If none are found, Medix exits with a clear message.

## Output formats

| Format | Default video | Default audio | Best for |
|--------|---------------|---------------|----------|
| **MP4** | H.264 | AAC | Universal playback |
| **MKV** | H.264 | AAC | Flexible container, multi-track |
| **WebM** | VP9 | Opus | Web streaming |
| **MOV** | H.264 | AAC | Apple ecosystem |
| **AVI** | H.264 | MP3 | Legacy compatibility |
| **TS** | H.264 | AAC | Broadcast / streaming |

You can override any of these defaults via [advanced
settings](/guides/advanced-settings/).

## Multi-format source handling

When a directory contains multiple input formats, Medix prompts you to pick
which ones to include:

```
? Multiple source formats found. Which should I convert?
  [x] .vob (12 files)
  [x] .mpg (3 files)
  [ ] .avi (1 file)
```

Unselected formats are skipped entirely.

## Copy vs re-encode

For both video and audio, `copy` is available as a codec option. This does a
container remux without re-encoding — fast, lossless, but only valid when
the source codec is compatible with the target container.
