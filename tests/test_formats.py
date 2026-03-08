from __future__ import annotations

import pytest

from medix.formats import (
    AUDIO_BITRATES,
    AUDIO_CODECS,
    FRAME_RATES,
    MEDIA_EXTENSIONS,
    OUTPUT_FORMATS,
    PRESETS,
    RESOLUTIONS,
    VIDEO_CODECS,
)


class TestMediaExtensions:
    def test_not_empty(self):
        assert len(MEDIA_EXTENSIONS) >= 15

    def test_all_start_with_dot(self):
        for ext in MEDIA_EXTENSIONS:
            assert ext.startswith("."), f"{ext} missing leading dot"

    def test_all_lowercase(self):
        for ext in MEDIA_EXTENSIONS:
            assert ext == ext.lower(), f"{ext} is not lowercase"

    def test_common_formats_included(self):
        for ext in (".mp4", ".mkv", ".avi", ".mov", ".vob", ".webm"):
            assert ext in MEDIA_EXTENSIONS, f"{ext} missing"


class TestOutputFormats:
    def test_not_empty(self):
        assert len(OUTPUT_FORMATS) >= 4

    @pytest.mark.parametrize("name", list(OUTPUT_FORMATS.keys()))
    def test_has_required_keys(self, name):
        fmt = OUTPUT_FORMATS[name]
        assert "extension" in fmt
        assert "description" in fmt
        assert "default_vcodec" in fmt
        assert "default_acodec" in fmt

    @pytest.mark.parametrize("name", list(OUTPUT_FORMATS.keys()))
    def test_extension_starts_with_dot(self, name):
        assert OUTPUT_FORMATS[name]["extension"].startswith(".")

    @pytest.mark.parametrize("name", list(OUTPUT_FORMATS.keys()))
    def test_default_codecs_are_valid(self, name):
        fmt = OUTPUT_FORMATS[name]
        assert fmt["default_vcodec"] in VIDEO_CODECS
        assert fmt["default_acodec"] in AUDIO_CODECS


class TestVideoCodecs:
    def test_has_copy_option(self):
        assert "copy" in VIDEO_CODECS

    def test_has_h264(self):
        assert "libx264" in VIDEO_CODECS

    def test_descriptions_not_empty(self):
        for codec, desc in VIDEO_CODECS.items():
            assert len(desc) > 0, f"{codec} has empty description"


class TestAudioCodecs:
    def test_has_copy_option(self):
        assert "copy" in AUDIO_CODECS

    def test_has_aac(self):
        assert "aac" in AUDIO_CODECS

    def test_descriptions_not_empty(self):
        for codec, desc in AUDIO_CODECS.items():
            assert len(desc) > 0, f"{codec} has empty description"


class TestResolutions:
    def test_has_original(self):
        assert "original" in RESOLUTIONS

    def test_dimensions_format(self):
        for key in RESOLUTIONS:
            if key == "original":
                continue
            w, h = key.split("x")
            assert int(w) > 0
            assert int(h) > 0


class TestFrameRates:
    def test_has_original(self):
        assert "original" in FRAME_RATES

    def test_numeric_values(self):
        for key in FRAME_RATES:
            if key == "original":
                continue
            assert int(key) > 0


class TestPresets:
    def test_has_medium(self):
        assert "medium" in PRESETS

    def test_known_presets(self):
        expected = {
            "ultrafast",
            "superfast",
            "veryfast",
            "faster",
            "fast",
            "medium",
            "slow",
            "slower",
            "veryslow",
        }
        assert set(PRESETS.keys()) == expected


class TestAudioBitrates:
    def test_has_auto(self):
        assert "auto" in AUDIO_BITRATES

    def test_bitrate_format(self):
        for key in AUDIO_BITRATES:
            if key == "auto":
                continue
            assert key.endswith("k"), f"{key} doesn't end with 'k'"
            assert int(key[:-1]) > 0
