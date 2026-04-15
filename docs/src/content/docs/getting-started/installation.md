---
title: Installation
description: Every way to install Medix — PyPI, pipx, from source, and more.
---

Medix is distributed on [PyPI](https://pypi.org/project/medix/) and mirrored
on [libraries.io](https://libraries.io/pypi/medix). Pick the method that
matches your workflow.

## From PyPI (recommended)

The simplest path. Works on any platform with Python 3.9+.

```bash
pip install medix
```

Upgrade later with:

```bash
pip install -U medix
```

## With pipx (isolated global install)

[pipx](https://pipx.pypa.io/) installs CLI tools into isolated environments
so they don't pollute your system Python. Strongly recommended if you use
Medix as a day-to-day tool.

```bash
pipx install medix
```

Upgrade:

```bash
pipx upgrade medix
```

Uninstall:

```bash
pipx uninstall medix
```

## From source

Clone the repo and install in editable mode. Useful if you're following
`main` or want to contribute.

```bash
git clone https://github.com/vineethkrishnan/medix.git
cd medix

python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -e .
```

## Development install

Same as source, but includes test and lint tooling.

```bash
pip install -e ".[dev]"
```

This pulls in `pytest`, `pytest-cov`, and `ruff`.

## From a Git tag / branch directly

```bash
pip install "git+https://github.com/vineethkrishnan/medix.git@main"
```

Replace `@main` with any tag (e.g. `@v1.3.0`) or branch.

## As a dependency in `pyproject.toml`

```toml
[project]
dependencies = [
  "medix>=1.3.0",
]
```

## Verify the install

```bash
medix --version
```

You should see the installed version printed. You can also invoke Medix as a
module:

```bash
python -m medix --version
```

## FFmpeg

Medix needs FFmpeg and `ffprobe` at runtime, but **you don't have to install
them first**. On first run, Medix detects your platform and offers to install
them automatically. If you'd rather do it yourself:

```bash
# macOS
brew install ffmpeg

# Ubuntu / Debian
sudo apt install ffmpeg

# Fedora
sudo dnf install ffmpeg

# Arch
sudo pacman -S ffmpeg

# Windows (winget)
winget install Gyan.FFmpeg
```

See [FFmpeg Auto-Install](/guides/ffmpeg-setup/) for the full list.

## Next steps

- [Quick Start](/getting-started/quick-start/) — convert your first file
- [CLI Usage](/guides/cli-usage/) — all the flags
- [Dry Run](/guides/dry-run/) — preview before converting
