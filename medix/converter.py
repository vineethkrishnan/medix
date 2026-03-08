from __future__ import annotations

import json
import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional, Tuple


@dataclass
class MediaInfo:
    path: Path
    duration: float
    size: int
    video_codec: str = ""
    audio_codec: str = ""
    resolution: str = ""
    frame_rate: float = 0.0
    bitrate: int = 0


@dataclass
class ConvertSettings:
    output_format: str = "MP4"
    video_codec: str = "libx264"
    audio_codec: str = "aac"
    resolution: str = "original"
    preset: str = "medium"
    crf: int = 23
    frame_rate: str = "original"
    audio_bitrate: str = "auto"
    output_dir: Optional[str] = None


def check_ffmpeg() -> bool:
    for cmd in ("ffmpeg", "ffprobe"):
        try:
            subprocess.run(
                [cmd, "-version"],
                capture_output=True,
                check=True,
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False
    return True


def probe_file(filepath: Path) -> Optional[MediaInfo]:
    try:
        cmd = [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(filepath),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)

        fmt = data.get("format", {})
        duration = float(fmt.get("duration", 0))
        size = int(fmt.get("size", 0))
        bitrate = int(fmt.get("bit_rate", 0) or 0)

        video_codec = ""
        audio_codec = ""
        resolution = ""
        frame_rate = 0.0

        for stream in data.get("streams", []):
            codec_type = stream.get("codec_type")
            if codec_type == "video" and not video_codec:
                video_codec = stream.get("codec_name", "")
                w = stream.get("width", 0)
                h = stream.get("height", 0)
                if w and h:
                    resolution = f"{w}x{h}"
                r_frame_rate = stream.get("r_frame_rate", "0/1")
                if "/" in r_frame_rate:
                    num, den = r_frame_rate.split("/")
                    if int(den) > 0:
                        frame_rate = round(int(num) / int(den), 2)
            elif codec_type == "audio" and not audio_codec:
                audio_codec = stream.get("codec_name", "")

        return MediaInfo(
            path=filepath,
            duration=duration,
            size=size,
            video_codec=video_codec,
            audio_codec=audio_codec,
            resolution=resolution,
            frame_rate=frame_rate,
            bitrate=bitrate,
        )
    except (subprocess.CalledProcessError, json.JSONDecodeError, ValueError, KeyError):
        return None


def build_command(
    input_path: Path,
    output_path: Path,
    settings: ConvertSettings,
) -> list:
    cmd = ["ffmpeg", "-i", str(input_path), "-y"]

    # Video codec
    if settings.video_codec == "copy":
        cmd.extend(["-c:v", "copy"])
    else:
        cmd.extend(["-c:v", settings.video_codec])

        if settings.video_codec in ("libx264", "libx265"):
            cmd.extend(["-crf", str(settings.crf)])
            cmd.extend(["-preset", settings.preset])

        if settings.resolution != "original":
            w, h = settings.resolution.split("x")
            # Scale while preserving aspect ratio, pad to exact dimensions
            vf = (
                f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
                f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2"
            )
            cmd.extend(["-vf", vf])

        if settings.frame_rate != "original":
            cmd.extend(["-r", settings.frame_rate])

    # Audio codec
    if settings.audio_codec == "copy":
        cmd.extend(["-c:a", "copy"])
    else:
        cmd.extend(["-c:a", settings.audio_codec])
        if settings.audio_bitrate != "auto":
            cmd.extend(["-b:a", settings.audio_bitrate])

    cmd.extend(["-progress", "pipe:1", "-nostats"])
    cmd.append(str(output_path))
    return cmd


def convert_file(
    input_path: Path,
    output_path: Path,
    settings: ConvertSettings,
    total_duration: float,
    on_progress: Optional[Callable[[float], None]] = None,
) -> Tuple[bool, str]:
    """Convert a file. Returns (success, error_message)."""
    cmd = build_command(input_path, output_path, settings)

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        stderr_lines: list = []

        def _drain_stderr():
            assert process.stderr is not None
            for line in process.stderr:
                stderr_lines.append(line)

        t = threading.Thread(target=_drain_stderr, daemon=True)
        t.start()

        assert process.stdout is not None
        for line in process.stdout:
            line = line.strip()
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            if key == "out_time_us" and on_progress and total_duration > 0:
                try:
                    current_us = int(value)
                    pct = min(current_us / (total_duration * 1_000_000), 1.0)
                    on_progress(pct)
                except ValueError:
                    pass
            elif key == "progress" and value == "end":
                if on_progress:
                    on_progress(1.0)

        process.wait()
        t.join(timeout=5)

        if process.returncode == 0:
            return True, ""

        err = "".join(stderr_lines).strip()
        last_lines = "\n".join(err.split("\n")[-3:]) if err else "Unknown error"
        return False, last_lines

    except Exception as e:
        return False, str(e)
