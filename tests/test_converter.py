from __future__ import annotations

import json
import subprocess
from unittest.mock import MagicMock, patch


from medix.converter import (
    ConvertSettings,
    MediaInfo,
    build_command,
    check_ffmpeg,
    convert_file,
    probe_file,
)


# ── ConvertSettings defaults ──────────────────────────────────────────


class TestConvertSettings:
    def test_defaults(self):
        s = ConvertSettings()
        assert s.output_format == "MP4"
        assert s.video_codec == "libx264"
        assert s.audio_codec == "aac"
        assert s.resolution == "original"
        assert s.preset == "medium"
        assert s.crf == 23
        assert s.frame_rate == "original"
        assert s.audio_bitrate == "auto"
        assert s.output_dir is None

    def test_custom_values(self):
        s = ConvertSettings(
            output_format="MKV",
            video_codec="libx265",
            audio_codec="libopus",
            resolution="1920x1080",
            preset="slow",
            crf=18,
            frame_rate="30",
            audio_bitrate="192k",
            output_dir="/tmp/out",
        )
        assert s.output_format == "MKV"
        assert s.crf == 18
        assert s.output_dir == "/tmp/out"


# ── MediaInfo ─────────────────────────────────────────────────────────


class TestMediaInfo:
    def test_creation(self, tmp_path):
        p = tmp_path / "video.mp4"
        p.touch()
        info = MediaInfo(path=p, duration=120.5, size=1024000)
        assert info.path == p
        assert info.duration == 120.5
        assert info.size == 1024000
        assert info.video_codec == ""
        assert info.resolution == ""


# ── build_command ─────────────────────────────────────────────────────


class TestBuildCommand:
    def _paths(self, tmp_path):
        inp = tmp_path / "input.vob"
        out = tmp_path / "output.mp4"
        return inp, out

    def test_default_settings(self, tmp_path):
        inp, out = self._paths(tmp_path)
        cmd = build_command(inp, out, ConvertSettings())
        assert cmd[0] == "ffmpeg"
        assert "-i" in cmd
        assert str(inp) in cmd
        assert str(out) == cmd[-1]
        assert "-c:v" in cmd
        assert "libx264" in cmd
        assert "-c:a" in cmd
        assert "aac" in cmd
        assert "-crf" in cmd
        assert "23" in cmd
        assert "-preset" in cmd
        assert "medium" in cmd

    def test_copy_codecs(self, tmp_path):
        inp, out = self._paths(tmp_path)
        settings = ConvertSettings(video_codec="copy", audio_codec="copy")
        cmd = build_command(inp, out, settings)
        v_idx = cmd.index("-c:v")
        assert cmd[v_idx + 1] == "copy"
        a_idx = cmd.index("-c:a")
        assert cmd[a_idx + 1] == "copy"
        assert "-crf" not in cmd
        assert "-preset" not in cmd

    def test_custom_resolution(self, tmp_path):
        inp, out = self._paths(tmp_path)
        settings = ConvertSettings(resolution="1280x720")
        cmd = build_command(inp, out, settings)
        assert "-vf" in cmd
        vf_idx = cmd.index("-vf")
        assert "1280" in cmd[vf_idx + 1]
        assert "720" in cmd[vf_idx + 1]

    def test_original_resolution_no_vf(self, tmp_path):
        inp, out = self._paths(tmp_path)
        settings = ConvertSettings(resolution="original")
        cmd = build_command(inp, out, settings)
        assert "-vf" not in cmd

    def test_custom_frame_rate(self, tmp_path):
        inp, out = self._paths(tmp_path)
        settings = ConvertSettings(frame_rate="60")
        cmd = build_command(inp, out, settings)
        r_idx = cmd.index("-r")
        assert cmd[r_idx + 1] == "60"

    def test_original_frame_rate_no_r(self, tmp_path):
        inp, out = self._paths(tmp_path)
        settings = ConvertSettings(frame_rate="original")
        cmd = build_command(inp, out, settings)
        assert "-r" not in cmd

    def test_audio_bitrate(self, tmp_path):
        inp, out = self._paths(tmp_path)
        settings = ConvertSettings(audio_bitrate="320k")
        cmd = build_command(inp, out, settings)
        ba_idx = cmd.index("-b:a")
        assert cmd[ba_idx + 1] == "320k"

    def test_auto_audio_bitrate_no_flag(self, tmp_path):
        inp, out = self._paths(tmp_path)
        settings = ConvertSettings(audio_bitrate="auto")
        cmd = build_command(inp, out, settings)
        assert "-b:a" not in cmd

    def test_h265_settings(self, tmp_path):
        inp, out = self._paths(tmp_path)
        settings = ConvertSettings(video_codec="libx265", preset="veryslow", crf=18)
        cmd = build_command(inp, out, settings)
        assert "libx265" in cmd
        assert "18" in cmd
        assert "veryslow" in cmd

    def test_vp9_no_crf_preset(self, tmp_path):
        inp, out = self._paths(tmp_path)
        settings = ConvertSettings(video_codec="libvpx-vp9")
        cmd = build_command(inp, out, settings)
        assert "libvpx-vp9" in cmd
        assert "-crf" not in cmd
        assert "-preset" not in cmd

    def test_progress_flags(self, tmp_path):
        inp, out = self._paths(tmp_path)
        cmd = build_command(inp, out, ConvertSettings())
        assert "-progress" in cmd
        assert "pipe:1" in cmd
        assert "-nostats" in cmd

    def test_overwrite_flag(self, tmp_path):
        inp, out = self._paths(tmp_path)
        cmd = build_command(inp, out, ConvertSettings())
        assert "-y" in cmd


# ── check_ffmpeg ──────────────────────────────────────────────────────


class TestCheckFfmpeg:
    @patch("medix.dependencies.shutil.which")
    def test_returns_true_when_both_present(self, mock_which):
        mock_which.side_effect = lambda cmd: f"/usr/bin/{cmd}"
        assert check_ffmpeg() is True

    @patch("medix.dependencies.shutil.which")
    def test_returns_false_when_ffmpeg_missing(self, mock_which):
        mock_which.side_effect = lambda cmd: (
            None if cmd == "ffmpeg" else f"/usr/bin/{cmd}"
        )
        assert check_ffmpeg() is False

    @patch("medix.dependencies.shutil.which")
    def test_returns_false_when_ffprobe_missing(self, mock_which):
        mock_which.side_effect = lambda cmd: (
            None if cmd == "ffprobe" else f"/usr/bin/{cmd}"
        )
        assert check_ffmpeg() is False


# ── probe_file ────────────────────────────────────────────────────────


class TestProbeFile:
    SAMPLE_PROBE_OUTPUT = json.dumps(
        {
            "format": {
                "duration": "125.5",
                "size": "5242880",
                "bit_rate": "334000",
            },
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "h264",
                    "width": 1920,
                    "height": 1080,
                    "r_frame_rate": "30/1",
                },
                {
                    "codec_type": "audio",
                    "codec_name": "aac",
                },
            ],
        }
    )

    @patch("medix.converter.subprocess.run")
    def test_parses_probe_output(self, mock_run, tmp_path):
        mock_run.return_value = MagicMock(stdout=self.SAMPLE_PROBE_OUTPUT, returncode=0)
        f = tmp_path / "test.mp4"
        f.touch()

        info = probe_file(f)
        assert info is not None
        assert info.duration == 125.5
        assert info.size == 5242880
        assert info.video_codec == "h264"
        assert info.audio_codec == "aac"
        assert info.resolution == "1920x1080"
        assert info.frame_rate == 30.0
        assert info.bitrate == 334000

    @patch("medix.converter.subprocess.run")
    def test_returns_none_on_error(self, mock_run, tmp_path):
        mock_run.side_effect = subprocess.CalledProcessError(1, "ffprobe")
        f = tmp_path / "bad.mp4"
        f.touch()
        assert probe_file(f) is None

    @patch("medix.converter.subprocess.run")
    def test_handles_audio_only(self, mock_run, tmp_path):
        data = json.dumps(
            {
                "format": {
                    "duration": "200.0",
                    "size": "1000000",
                    "bit_rate": "128000",
                },
                "streams": [{"codec_type": "audio", "codec_name": "mp3"}],
            }
        )
        mock_run.return_value = MagicMock(stdout=data, returncode=0)
        f = tmp_path / "audio.mp3"
        f.touch()
        info = probe_file(f)
        assert info is not None
        assert info.video_codec == ""
        assert info.audio_codec == "mp3"
        assert info.resolution == ""


# ── convert_file ──────────────────────────────────────────────────────


class TestConvertFile:
    @patch("medix.converter.subprocess.Popen")
    def test_successful_conversion(self, mock_popen, tmp_path):
        inp = tmp_path / "in.vob"
        out = tmp_path / "out.mp4"
        inp.touch()

        mock_proc = MagicMock()
        mock_proc.stdout = iter(["out_time_us=60000000\n", "progress=end\n"])
        mock_proc.stderr = iter([])
        mock_proc.returncode = 0
        mock_proc.wait.return_value = 0
        mock_popen.return_value = mock_proc

        progress_values = []
        ok, err = convert_file(
            inp,
            out,
            ConvertSettings(),
            total_duration=120.0,
            on_progress=lambda p: progress_values.append(p),
        )
        assert ok is True
        assert err == ""
        assert len(progress_values) > 0

    @patch("medix.converter.subprocess.Popen")
    def test_failed_conversion(self, mock_popen, tmp_path):
        inp = tmp_path / "in.vob"
        out = tmp_path / "out.mp4"
        inp.touch()

        mock_proc = MagicMock()
        mock_proc.stdout = iter([])
        mock_proc.stderr = iter(["Error: something went wrong\n"])
        mock_proc.returncode = 1
        mock_proc.wait.return_value = 1
        mock_popen.return_value = mock_proc

        ok, err = convert_file(inp, out, ConvertSettings(), total_duration=60.0)
        assert ok is False
        assert "something went wrong" in err
