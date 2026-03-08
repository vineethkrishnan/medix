from __future__ import annotations

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from medix.cli import (
    _fmt_duration,
    _fmt_size,
    _resolve_output_path,
    discover_files,
    main,
)
from medix.converter import MediaInfo


# ── _fmt_duration ─────────────────────────────────────────────────────


class TestFmtDuration:
    @pytest.mark.parametrize(
        "seconds, expected",
        [
            (0, "--:--"),
            (-5, "--:--"),
            (59, "00:59"),
            (60, "01:00"),
            (90, "01:30"),
            (3599, "59:59"),
            (3600, "01:00:00"),
            (3661, "01:01:01"),
            (86399, "23:59:59"),
        ],
    )
    def test_formats(self, seconds, expected):
        assert _fmt_duration(seconds) == expected


# ── _fmt_size ─────────────────────────────────────────────────────────


class TestFmtSize:
    @pytest.mark.parametrize(
        "size, expected_suffix",
        [
            (0, "N/A"),
            (500, "B"),
            (1024, "KB"),
            (1048576, "MB"),
            (1073741824, "GB"),
        ],
    )
    def test_units(self, size, expected_suffix):
        result = _fmt_size(size)
        if expected_suffix == "N/A":
            assert result == "N/A"
        else:
            assert result.endswith(expected_suffix)

    def test_negative(self):
        assert _fmt_size(-100) == "N/A"


# ── discover_files ────────────────────────────────────────────────────


class TestDiscoverFiles:
    def _populate(self, tmp_path):
        (tmp_path / "video.mp4").touch()
        (tmp_path / "audio.mkv").touch()
        (tmp_path / "document.txt").touch()
        (tmp_path / "image.png").touch()
        sub = tmp_path / "subdir"
        sub.mkdir()
        (sub / "nested.avi").touch()
        (sub / "notes.md").touch()
        return tmp_path

    def test_single_file_media(self, tmp_path):
        f = tmp_path / "test.mp4"
        f.touch()
        assert discover_files(f) == [f]

    def test_single_file_non_media(self, tmp_path):
        f = tmp_path / "readme.txt"
        f.touch()
        assert discover_files(f) == []

    def test_directory_flat(self, tmp_path):
        self._populate(tmp_path)
        files = discover_files(tmp_path)
        names = {f.name for f in files}
        assert "video.mp4" in names
        assert "audio.mkv" in names
        assert "document.txt" not in names
        assert "nested.avi" not in names

    def test_directory_recursive(self, tmp_path):
        self._populate(tmp_path)
        files = discover_files(tmp_path, recursive=True)
        names = {f.name for f in files}
        assert "video.mp4" in names
        assert "audio.mkv" in names
        assert "nested.avi" in names
        assert "document.txt" not in names

    def test_empty_directory(self, tmp_path):
        assert discover_files(tmp_path) == []

    def test_all_supported_extensions(self, tmp_path):
        from medix.formats import MEDIA_EXTENSIONS

        for ext in MEDIA_EXTENSIONS:
            (tmp_path / f"file{ext}").touch()
        files = discover_files(tmp_path)
        assert len(files) == len(MEDIA_EXTENSIONS)


# ── _resolve_output_path ──────────────────────────────────────────────


class TestResolveOutputPath:
    def test_flat_output(self, tmp_path):
        info = MediaInfo(path=tmp_path / "video.vob", duration=60, size=1000)
        fmt_def = {"extension": ".mp4"}
        out_dir = tmp_path / "converted"
        out_dir.mkdir()

        result = _resolve_output_path(info, fmt_def, out_dir, tmp_path, recursive=False)
        assert result.name == "video.mp4"
        assert result.parent == out_dir

    def test_avoids_overwrite(self, tmp_path):
        info = MediaInfo(path=tmp_path / "video.vob", duration=60, size=1000)
        fmt_def = {"extension": ".mp4"}
        out_dir = tmp_path / "converted"
        out_dir.mkdir()
        (out_dir / "video.mp4").touch()

        result = _resolve_output_path(info, fmt_def, out_dir, tmp_path, recursive=False)
        assert result.name == "video_1.mp4"

    def test_recursive_preserves_structure(self, tmp_path):
        sub = tmp_path / "season1"
        sub.mkdir()
        info = MediaInfo(path=sub / "ep01.vob", duration=60, size=1000)
        fmt_def = {"extension": ".mp4"}
        out_dir = tmp_path / "converted"
        out_dir.mkdir()

        result = _resolve_output_path(info, fmt_def, out_dir, tmp_path, recursive=True)
        assert result == out_dir / "season1" / "ep01.mp4"


# ── CLI runner ────────────────────────────────────────────────────────


class TestCLIRunner:
    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "medix" in result.output.lower()

    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "--dry-run" in result.output
        assert "--recursive" in result.output
        assert "--output" in result.output

    def test_nonexistent_path(self):
        runner = CliRunner()
        result = runner.invoke(main, ["/nonexistent/path/xyz"])
        assert result.exit_code != 0

    @patch("medix.cli.find_missing_tools", return_value=[])
    def test_no_media_files(self, _, tmp_path):
        (tmp_path / "readme.txt").write_text("hello")
        runner = CliRunner()
        result = runner.invoke(main, [str(tmp_path)])
        assert result.exit_code != 0
        assert "No media files" in result.output

    @patch("medix.cli.find_missing_tools", return_value=[])
    @patch("medix.cli.probe_file")
    @patch("medix.cli.questionary")
    def test_dry_run_flag(self, mock_q, mock_probe, _, tmp_path):
        media = tmp_path / "test.mp4"
        media.touch()

        mock_probe.return_value = MediaInfo(
            path=media, duration=60.0, size=1000000, resolution="1920x1080"
        )

        mock_q.select.return_value.ask.return_value = "MP4"
        mock_q.confirm.return_value.ask.return_value = False
        mock_q.Style = lambda x: x

        runner = CliRunner()
        result = runner.invoke(main, [str(media), "--dry-run"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.output
        assert "No files were converted" in result.output
