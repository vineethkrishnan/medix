from __future__ import annotations

from unittest.mock import patch


from medix.dependencies import (
    DOWNLOAD_URLS,
    REQUIRED_TOOLS,
    PackageManager,
    detect_package_manager,
    find_missing_tools,
    get_manual_install_hint,
    get_platform_info,
    install_ffmpeg,
    verify_installation,
)


# ── PackageManager ────────────────────────────────────────────────────


class TestPackageManager:
    def test_install_cmd(self):
        pm = PackageManager("Homebrew", "brew", ["install", "ffmpeg"])
        assert pm.install_cmd() == ["brew", "install", "ffmpeg"]

    def test_install_cmd_with_sudo(self):
        pm = PackageManager("APT", "sudo", ["apt-get", "install", "-y", "ffmpeg"])
        assert pm.install_cmd() == ["sudo", "apt-get", "install", "-y", "ffmpeg"]


# ── get_platform_info ─────────────────────────────────────────────────


class TestGetPlatformInfo:
    def test_returns_tuple(self):
        os_name, arch = get_platform_info()
        assert isinstance(os_name, str)
        assert isinstance(arch, str)
        assert len(os_name) > 0
        assert len(arch) > 0

    @patch("medix.dependencies.platform.system", return_value="Darwin")
    @patch("medix.dependencies.platform.machine", return_value="arm64")
    def test_darwin_arm64(self, *_):
        assert get_platform_info() == ("darwin", "arm64")

    @patch("medix.dependencies.platform.system", return_value="Linux")
    @patch("medix.dependencies.platform.machine", return_value="x86_64")
    def test_linux_x86(self, *_):
        assert get_platform_info() == ("linux", "x86_64")

    @patch("medix.dependencies.platform.system", return_value="Windows")
    @patch("medix.dependencies.platform.machine", return_value="AMD64")
    def test_windows(self, *_):
        assert get_platform_info() == ("windows", "amd64")


# ── find_missing_tools ────────────────────────────────────────────────


class TestFindMissingTools:
    @patch("medix.dependencies.shutil.which")
    def test_nothing_missing(self, mock_which):
        mock_which.side_effect = lambda cmd: f"/usr/bin/{cmd}"
        result = find_missing_tools()
        assert result == []

    @patch("medix.dependencies.shutil.which")
    def test_all_missing(self, mock_which):
        mock_which.return_value = None
        result = find_missing_tools()
        names = {t.name for t in result}
        assert names == set(REQUIRED_TOOLS)

    @patch("medix.dependencies.shutil.which")
    def test_ffprobe_missing(self, mock_which):
        mock_which.side_effect = lambda cmd: (
            None if cmd == "ffprobe" else "/usr/bin/ffmpeg"
        )
        result = find_missing_tools()
        assert len(result) == 1
        assert result[0].name == "ffprobe"


# ── detect_package_manager ────────────────────────────────────────────


class TestDetectPackageManager:
    @patch("medix.dependencies.get_platform_info", return_value=("darwin", "arm64"))
    @patch("medix.dependencies._has")
    def test_macos_homebrew(self, mock_has, _):
        mock_has.side_effect = lambda cmd: cmd == "brew"
        pm = detect_package_manager()
        assert pm is not None
        assert pm.name == "Homebrew"
        assert pm.install_cmd() == ["brew", "install", "ffmpeg"]

    @patch("medix.dependencies.get_platform_info", return_value=("darwin", "arm64"))
    @patch("medix.dependencies._has")
    def test_macos_macports(self, mock_has, _):
        mock_has.side_effect = lambda cmd: cmd == "port"
        pm = detect_package_manager()
        assert pm is not None
        assert pm.name == "MacPorts"

    @patch("medix.dependencies.get_platform_info", return_value=("linux", "x86_64"))
    @patch("medix.dependencies._has")
    def test_linux_apt(self, mock_has, _):
        mock_has.side_effect = lambda cmd: cmd == "apt-get"
        pm = detect_package_manager()
        assert pm is not None
        assert pm.name == "APT"
        assert "apt-get" in pm.install_cmd()

    @patch("medix.dependencies.get_platform_info", return_value=("linux", "x86_64"))
    @patch("medix.dependencies._has")
    def test_linux_dnf(self, mock_has, _):
        mock_has.side_effect = lambda cmd: cmd == "dnf"
        pm = detect_package_manager()
        assert pm is not None
        assert pm.name == "DNF"

    @patch("medix.dependencies.get_platform_info", return_value=("linux", "x86_64"))
    @patch("medix.dependencies._has")
    def test_linux_pacman(self, mock_has, _):
        mock_has.side_effect = lambda cmd: cmd == "pacman"
        pm = detect_package_manager()
        assert pm is not None
        assert pm.name == "Pacman"

    @patch("medix.dependencies.get_platform_info", return_value=("windows", "amd64"))
    @patch("medix.dependencies._has")
    def test_windows_winget(self, mock_has, _):
        mock_has.side_effect = lambda cmd: cmd == "winget"
        pm = detect_package_manager()
        assert pm is not None
        assert pm.name == "winget"
        assert "Gyan.FFmpeg" in pm.install_cmd()

    @patch("medix.dependencies.get_platform_info", return_value=("windows", "amd64"))
    @patch("medix.dependencies._has")
    def test_windows_choco(self, mock_has, _):
        mock_has.side_effect = lambda cmd: cmd == "choco"
        pm = detect_package_manager()
        assert pm is not None
        assert pm.name == "Chocolatey"

    @patch("medix.dependencies.get_platform_info", return_value=("windows", "amd64"))
    @patch("medix.dependencies._has")
    def test_windows_scoop(self, mock_has, _):
        mock_has.side_effect = lambda cmd: cmd == "scoop"
        pm = detect_package_manager()
        assert pm is not None
        assert pm.name == "Scoop"

    @patch("medix.dependencies.get_platform_info", return_value=("darwin", "arm64"))
    @patch("medix.dependencies._has", return_value=False)
    def test_none_when_no_pm(self, *_):
        assert detect_package_manager() is None

    @patch("medix.dependencies.get_platform_info", return_value=("freebsd", "amd64"))
    @patch("medix.dependencies._has", return_value=True)
    def test_unsupported_os(self, *_):
        assert detect_package_manager() is None


# ── install_ffmpeg ────────────────────────────────────────────────────


class TestInstallFfmpeg:
    @patch("medix.dependencies.subprocess.run")
    def test_success(self, mock_run):
        mock_run.return_value = type(
            "R", (), {"returncode": 0, "stdout": "done", "stderr": ""}
        )()
        pm = PackageManager("Homebrew", "brew", ["install", "ffmpeg"])
        ok, output = install_ffmpeg(pm)
        assert ok is True
        assert "done" in output

    @patch("medix.dependencies.subprocess.run")
    def test_failure(self, mock_run):
        mock_run.return_value = type(
            "R", (), {"returncode": 1, "stdout": "", "stderr": "error: not found"}
        )()
        pm = PackageManager("Homebrew", "brew", ["install", "ffmpeg"])
        ok, output = install_ffmpeg(pm)
        assert ok is False
        assert "not found" in output

    @patch("medix.dependencies.subprocess.run")
    def test_timeout(self, mock_run):
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired(cmd="brew", timeout=300)
        pm = PackageManager("Homebrew", "brew", ["install", "ffmpeg"])
        ok, output = install_ffmpeg(pm)
        assert ok is False
        assert "timed out" in output.lower()

    @patch("medix.dependencies.subprocess.run")
    def test_command_not_found(self, mock_run):
        mock_run.side_effect = FileNotFoundError()
        pm = PackageManager("Homebrew", "brew", ["install", "ffmpeg"])
        ok, output = install_ffmpeg(pm)
        assert ok is False


# ── get_manual_install_hint ───────────────────────────────────────────


class TestGetManualInstallHint:
    @patch("medix.dependencies.get_platform_info", return_value=("darwin", "arm64"))
    def test_macos_hint(self, _):
        hint = get_manual_install_hint()
        assert "brew" in hint.lower()
        assert "brew.sh" in hint

    @patch("medix.dependencies.get_platform_info", return_value=("linux", "x86_64"))
    def test_linux_hint(self, _):
        hint = get_manual_install_hint()
        assert "apt" in hint.lower()

    @patch("medix.dependencies.get_platform_info", return_value=("windows", "amd64"))
    def test_windows_hint(self, _):
        hint = get_manual_install_hint()
        assert "winget" in hint.lower()

    @patch("medix.dependencies.get_platform_info", return_value=("haiku", "x86_64"))
    def test_unknown_os_hint(self, _):
        hint = get_manual_install_hint()
        assert "ffmpeg.org" in hint


# ── verify_installation ───────────────────────────────────────────────


class TestVerifyInstallation:
    @patch("medix.dependencies.shutil.which")
    def test_delegates_to_find_missing(self, mock_which):
        mock_which.return_value = "/usr/bin/ffmpeg"
        assert verify_installation() == []


# ── DOWNLOAD_URLS ─────────────────────────────────────────────────────


class TestConstants:
    def test_required_tools_not_empty(self):
        assert len(REQUIRED_TOOLS) >= 2

    def test_download_urls_cover_platforms(self):
        assert "darwin" in DOWNLOAD_URLS
        assert "linux" in DOWNLOAD_URLS
        assert "windows" in DOWNLOAD_URLS
