---
title: Dry Run Mode
description: Preview conversions without touching disk using --dry-run.
---

Dry-run mode lets you walk through the entire interactive flow and see the
planned conversion — without writing a single file.

## When to use it

- You're running Medix against a large tree and want to verify the target
  list before committing 30 minutes of encode time.
- You want to capture the exact `ffmpeg` command Medix would run, for use in
  a script or to understand how codec settings map to flags.
- You're unsure whether your settings will do what you expect.
- You're writing a CI job and want to verify configuration without burning
  compute.

## Usage

```bash
medix /path/to/videos/ --dry-run
```

Or the short form:

```bash
medix /path/to/videos/ -n
```

## What happens

Medix runs the normal flow:

1. Scans and discovers files
2. Asks you to pick source formats (if multiple)
3. Asks for the output format
4. Optionally asks for advanced settings
5. Builds the conversion plan

...then stops before invoking `ffmpeg`, printing:

- The file mapping (inputs → outputs)
- A representative `ffmpeg` command built from your settings
- A summary of what *would* have been converted

## Example output

```
Dry run — no files will be written.

Input                         →   Output
─────────────────────────────────────────────────────────
clip_01.vob                   →   converted/clip_01.mp4
clip_02.vob                   →   converted/clip_02.mp4
clip_03.vob                   →   converted/clip_03.mp4

Example ffmpeg command:
  ffmpeg -i clip_01.vob -c:v libx264 -preset medium -crf 23 \
         -c:a aac -b:a 192k converted/clip_01.mp4
```

## Combine with other flags

Dry-run composes with every other flag:

```bash
# Recursive dry run
medix ~/Videos/ -r --dry-run

# Dry run with custom output
medix ~/Videos/ -o ~/Converted/ --dry-run
```
