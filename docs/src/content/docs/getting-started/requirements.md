---
title: Requirements
description: System and software prerequisites for running Medix.
---

## Runtime requirements

| Dependency | Minimum | Check |
|-----------|---------|-------|
| **Python** | 3.9+ | `python3 --version` |
| **FFmpeg** | 4.4+ | `ffmpeg -version` |
| **ffprobe** | bundled with FFmpeg | `ffprobe -version` |

:::tip[Don't have FFmpeg?]
You don't need to install it manually. On first run, Medix detects your
platform and offers to install FFmpeg via the package manager it finds. See
[FFmpeg Auto-Install](/guides/ffmpeg-setup/).
:::

## Supported Python versions

Medix is tested in CI on **Python 3.9, 3.10, 3.11, 3.12, and 3.13**.

## Supported platforms

| OS | Package managers detected |
|----|---------------------------|
| **macOS** 12+ | Homebrew, MacPorts |
| **Ubuntu** 20.04+ / Debian 11+ | APT |
| **Fedora / RHEL** | DNF, YUM |
| **Arch Linux** | Pacman |
| **Windows** 10+ | winget, Chocolatey, Scoop |

## Python dependencies

Installed automatically when you `pip install medix`:

- `click>=8.0` — command-line argument parsing
- `rich>=13.0` — terminal UI (tables, panels, progress bars)
- `questionary>=2.0` — interactive prompts

Development extras (`pip install medix[dev]`):

- `pytest>=7.0`
- `pytest-cov>=4.0`
- `ruff>=0.4`
