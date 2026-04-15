---
title: FFmpeg Auto-Install
description: How Medix detects and installs FFmpeg for you.
---

Medix needs `ffmpeg` and `ffprobe` to do actual conversion, but you don't
have to install them first. On every run, Medix checks whether both binaries
are on `PATH`. If not, it:

1. Detects your operating system and architecture
2. Probes for a supported package manager
3. Offers to run the right install command for you

You can always say no and install manually.

## Supported managers

| Platform | Detected managers |
|----------|-------------------|
| **macOS** | Homebrew, MacPorts |
| **Debian / Ubuntu** | APT |
| **Fedora / RHEL / CentOS** | DNF, YUM |
| **Arch Linux / Manjaro** | Pacman |
| **Windows** | winget, Chocolatey, Scoop |

## Manual install reference

If you'd rather install FFmpeg yourself:

### macOS

```bash
brew install ffmpeg
```

### Ubuntu / Debian

```bash
sudo apt update
sudo apt install ffmpeg
```

### Fedora

```bash
sudo dnf install ffmpeg
```

### RHEL / CentOS

Enable RPM Fusion first, then:

```bash
sudo dnf install ffmpeg
```

### Arch Linux

```bash
sudo pacman -S ffmpeg
```

### Windows — winget

```powershell
winget install Gyan.FFmpeg
```

### Windows — Chocolatey

```powershell
choco install ffmpeg
```

### Windows — Scoop

```powershell
scoop install ffmpeg
```

## Verifying the install

```bash
ffmpeg -version
ffprobe -version
```

Both should print version info. If either says "command not found", make
sure your shell has re-loaded `PATH` after install (open a new terminal).

## Troubleshooting

**"FFmpeg is installed but Medix can't find it"** — make sure it's on
`PATH`. On Windows, check `Environment Variables → PATH`. On macOS/Linux,
run `which ffmpeg` — it should print a path.

**"Package manager not detected"** — Medix falls back to printing manual
install instructions for your platform. File an issue if you think a
manager should be supported.
