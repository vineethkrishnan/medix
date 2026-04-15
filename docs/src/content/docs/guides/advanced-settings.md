---
title: Advanced Settings
description: Tune video codec, resolution, frame rate, CRF, and more.
---

After picking an output format, Medix asks whether you want to configure
advanced settings. Say yes and you get control over every knob that matters
for modern encoding.

## Video codec

| Option | libffmpeg name | Notes |
|--------|----------------|-------|
| **H.264** | `libx264` | Best compatibility, default for most formats |
| **H.265** | `libx265` | Better compression, requires modern decoders |
| **VP9** | `libvpx-vp9` | Open, default for WebM |
| **AV1** | `libaom-av1` | Best compression, slow encode |
| **MPEG-4** | `mpeg4` | Legacy |
| **copy** | — | Container remux, no re-encode |

## Audio codec

| Option | Notes |
|--------|-------|
| **AAC** | Default for MP4/MKV/MOV/TS |
| **MP3** | Legacy-friendly |
| **Opus** | Default for WebM, best quality/bitrate ratio |
| **AC3** | Surround-compatible |
| **FLAC** | Lossless |
| **copy** | No re-encode |

## Resolution

| Option | Dimensions |
|--------|-----------|
| Keep original | (no scaling) |
| 4K | 3840 × 2160 |
| 2K | 2560 × 1440 |
| 1080p | 1920 × 1080 |
| 720p | 1280 × 720 |
| 480p | 854 × 480 |
| 360p | 640 × 360 |

Aspect ratio is preserved.

## Frame rate

Keep original, or cap to 24, 25, 30, 48, or 60 fps.

## Encoding preset

Only relevant for `libx264` and `libx265`. Controls the speed/compression
trade-off:

```
ultrafast  superfast  veryfast  faster  fast  medium  slow  slower  veryslow
← faster / larger                                  smaller / slower →
```

`medium` is the default and a good balance.

## CRF (Constant Rate Factor)

Range: **0–51** for H.264 / H.265.

| CRF | Quality |
|-----|---------|
| 0 | Lossless |
| 18 | Visually lossless |
| 23 | Default, very good |
| 28 | Smaller files, still decent |
| 51 | Worst quality |

Lower CRF = higher quality = larger file.

## Audio bitrate

Auto (codec-dependent default), or explicit: **96k, 128k, 192k, 256k, 320k**.

## How it maps to ffmpeg

Medix builds an `ffmpeg` command from your choices. A typical result:

```bash
ffmpeg -i input.vob \
  -c:v libx264 -preset medium -crf 23 \
  -c:a aac -b:a 192k \
  output.mp4
```

You can see the exact command Medix would run with `--dry-run`. See
[Dry Run Mode](/guides/dry-run/).
