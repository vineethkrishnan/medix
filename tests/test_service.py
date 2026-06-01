from __future__ import annotations

import os
import plistlib

import pytest

from medix import service


@pytest.fixture
def temp_config(tmp_path, monkeypatch):
    monkeypatch.setenv("MEDIX_CONFIG_DIR", str(tmp_path))
    return tmp_path


class TestState:
    def test_roundtrip(self, temp_config):
        service._write_state(4321, "127.0.0.1", 8756)
        state = service._read_state()
        assert state == {"pid": 4321, "host": "127.0.0.1", "port": 8756}

    def test_missing_returns_none(self, temp_config):
        assert service._read_state() is None

    def test_clear(self, temp_config):
        service._write_state(1, "127.0.0.1", 8756)
        service._clear_state()
        assert service._read_state() is None


class TestPidAlive:
    def test_zero_is_not_alive(self):
        assert service._pid_alive(0) is False

    def test_current_process_is_alive(self):
        assert service._pid_alive(os.getpid()) is True

    def test_unused_pid_is_not_alive(self):
        assert service._pid_alive(2_000_000_000) is False


class TestStatus:
    def test_stopped_without_state(self, temp_config):
        result, info = service.status_background()
        assert result == "stopped"
        assert info is None

    def test_running_with_live_pid(self, temp_config):
        service._write_state(os.getpid(), "127.0.0.1", 8756)
        result, info = service.status_background()
        assert result == "running"
        assert info["port"] == 8756

    def test_stale_pid_reads_as_stopped(self, temp_config):
        service._write_state(2_000_000_000, "127.0.0.1", 8756)
        result, _ = service.status_background()
        assert result == "stopped"


class TestLaunchdPlist:
    def test_is_valid_plist(self):
        plist = service.build_launchd_plist("127.0.0.1", 9001)
        parsed = plistlib.loads(plist.encode("utf-8"))
        assert parsed["Label"] == service.LAUNCHD_LABEL
        assert parsed["RunAtLoad"] is True
        assert parsed["KeepAlive"] is True

    def test_program_args_invoke_module_with_port(self):
        parsed = plistlib.loads(
            service.build_launchd_plist("127.0.0.1", 9001).encode("utf-8")
        )
        args = parsed["ProgramArguments"]
        assert "-m" in args
        assert "medix.gui" in args
        assert "9001" in args
        assert "--no-browser" in args
