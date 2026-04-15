---
title: CLI Usage
description: All the ways to invoke Medix from the command line.
---

Medix exposes a single command: `medix`.

## Synopsis

```
medix [OPTIONS] PATH
```

`PATH` can be a single media file or a directory.

## Options

| Flag | Short | Description |
|------|-------|-------------|
| `--output PATH` | `-o` | Output directory. Default: `<input>/converted/` |
| `--recursive` | `-r` | Recurse into subdirectories |
| `--dry-run` | `-n` | Show what would happen without converting |
| `--version` | | Print version and exit |
| `--help` | `-h` | Show help and exit |

## Examples

### Single file

```bash
medix video.mp4
```

### Directory (non-recursive)

```bash
medix ~/Videos/
```

Only scans files directly under `~/Videos/`.

### Directory (recursive)

```bash
medix ~/Videos/ -r
```

Scans every subdirectory too.

### Custom output directory

```bash
medix ~/Videos/ -o ~/Converted/
```

If the directory doesn't exist, Medix creates it.

### Dry run

```bash
medix ~/Videos/ --dry-run
```

Shows the mapping of inputs → outputs and the ffmpeg command that would be
executed. No files are written. See [Dry Run Mode](/guides/dry-run/).

## Module invocation

Medix can also be invoked as a Python module, useful in environments where
`PATH` shimming isn't available:

```bash
python -m medix /path/to/videos/
```

## Output path rules

| Scenario | Output location |
|----------|-----------------|
| File input, no `-o` | `<file_parent>/converted/` |
| Directory input, no `-o` | `<input>/converted/` |
| Any input with `-o <dir>` | `<dir>/` |

Filename collisions are resolved by appending an incrementing counter, so
existing files are never overwritten.

## Exit behaviour

Medix prints a final summary table showing successful and failed files. Any
failures include the ffmpeg error output so you can diagnose issues.
