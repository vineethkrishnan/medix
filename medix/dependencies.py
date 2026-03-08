from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass
from typing import List, Optional


REQUIRED_TOOLS = ("ffmpeg", "ffprobe")


@dataclass
class MissingTool:
    name: str
    path: Optional[str] = None


@dataclass
class PackageManager:
    name: str
    command: str
    install_args: List[str]

    def install_cmd(self) -> List[str]:
        return [self.command, *self.install_args]


# ──────────────────────────────────────────────── detection helpers


def get_platform_info() -> tuple[str, str]:
    """Return (os_name, architecture) e.g. ('darwin', 'arm64')."""
    os_name = platform.system().lower()
    arch = platform.machine().lower()
    return os_name, arch


def find_missing_tools() -> List[MissingTool]:
    missing = []
    for tool in REQUIRED_TOOLS:
        path = shutil.which(tool)
        if path is None:
            missing.append(MissingTool(name=tool))
    return missing


def _has(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def detect_package_manager() -> Optional[PackageManager]:
    os_name, _ = get_platform_info()

    if os_name == "darwin":
        if _has("brew"):
            return PackageManager("Homebrew", "brew", ["install", "ffmpeg"])
        if _has("port"):
            return PackageManager("MacPorts", "sudo", ["port", "install", "ffmpeg"])

    elif os_name == "linux":
        if _has("apt-get"):
            return PackageManager(
                "APT", "sudo", ["apt-get", "install", "-y", "ffmpeg"]
            )
        if _has("dnf"):
            return PackageManager("DNF", "sudo", ["dnf", "install", "-y", "ffmpeg"])
        if _has("yum"):
            return PackageManager("YUM", "sudo", ["yum", "install", "-y", "ffmpeg"])
        if _has("pacman"):
            return PackageManager(
                "Pacman", "sudo", ["pacman", "-S", "--noconfirm", "ffmpeg"]
            )
        if _has("zypper"):
            return PackageManager(
                "Zypper", "sudo", ["zypper", "install", "-y", "ffmpeg"]
            )
        if _has("apk"):
            return PackageManager("APK", "sudo", ["apk", "add", "ffmpeg"])
        if _has("snap"):
            return PackageManager("Snap", "sudo", ["snap", "install", "ffmpeg"])

    elif os_name == "windows":
        if _has("winget"):
            return PackageManager(
                "winget", "winget", ["install", "--id", "Gyan.FFmpeg", "-e"]
            )
        if _has("choco"):
            return PackageManager("Chocolatey", "choco", ["install", "ffmpeg", "-y"])
        if _has("scoop"):
            return PackageManager("Scoop", "scoop", ["install", "ffmpeg"])

    return None


# ──────────────────────────────────────────── installation


def install_ffmpeg(pm: PackageManager) -> tuple[bool, str]:
    """Run the package manager install command. Returns (success, output)."""
    cmd = pm.install_cmd()
    try:
        result = subprocess.run(
            cmd,
            text=True,
            capture_output=True,
            timeout=300,
        )
        combined = (result.stdout or "") + (result.stderr or "")
        if result.returncode == 0:
            return True, combined.strip()
        return False, combined.strip()
    except subprocess.TimeoutExpired:
        return False, "Installation timed out after 5 minutes."
    except FileNotFoundError:
        return False, f"Package manager command not found: {cmd[0]}"
    except Exception as e:
        return False, str(e)


def verify_installation() -> List[MissingTool]:
    """Re-check after installation (clear shutil cache on 3.12+)."""
    if sys.version_info >= (3, 12) and hasattr(shutil.which, "cache_clear"):
        shutil.which.cache_clear()  # type: ignore[attr-defined]
    return find_missing_tools()


# ──────────────────────────────────────── download URLs for manual install


DOWNLOAD_URLS = {
    "darwin": "https://formulae.brew.sh/formula/ffmpeg  (brew install ffmpeg)",
    "linux": "https://ffmpeg.org/download.html#build-linux",
    "windows": "https://www.gyan.dev/ffmpeg/builds/",
}


def get_manual_install_hint() -> str:
    os_name, arch = get_platform_info()
    url = DOWNLOAD_URLS.get(os_name, "https://ffmpeg.org/download.html")
    hints = [f"  Download: {url}"]

    if os_name == "darwin":
        hints.insert(0, "  Install Homebrew first: https://brew.sh")
        hints.append("  Then run: brew install ffmpeg")
    elif os_name == "linux":
        hints.append("  Most distros: sudo apt install ffmpeg  (or your package manager)")
    elif os_name == "windows":
        hints.append("  Or use: winget install Gyan.FFmpeg")

    return "\n".join(hints)
