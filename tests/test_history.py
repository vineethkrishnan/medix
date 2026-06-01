from __future__ import annotations

import time

import pytest

from medix import history
from medix.history import HistoryRecord


@pytest.fixture
def temp_history(tmp_path, monkeypatch):
    monkeypatch.setenv("MEDIX_CONFIG_DIR", str(tmp_path))
    return tmp_path


def _record(name: str, timestamp: float, status: str = "success") -> HistoryRecord:
    return HistoryRecord(
        timestamp=timestamp,
        input_name=name,
        input_path=f"/in/{name}",
        output_path=f"/out/{name}.mp4",
        output_format="MP4",
        video_codec="libx264",
        audio_codec="aac",
        media_duration=120.0,
        input_size=1000,
        output_size=800,
        elapsed=4.2,
        status=status,
    )


class TestPersistence:
    def test_add_and_read_roundtrip(self, temp_history):
        history.add_record(_record("a.ts", time.time()))
        records = history.list_records()
        assert len(records) == 1
        assert records[0].input_name == "a.ts"

    def test_missing_file_returns_empty(self, temp_history):
        assert history.list_records() == []

    def test_corrupt_file_returns_empty(self, temp_history):
        history.history_path().parent.mkdir(parents=True, exist_ok=True)
        history.history_path().write_text("not json", encoding="utf-8")
        assert history.list_records() == []


class TestWindowFiltering:
    def test_filters_out_old_records(self, temp_history):
        now = time.time()
        history.add_record(_record("recent.ts", now - 3600))
        history.add_record(_record("old.ts", now - 10 * 24 * 3600))

        within_day = history.list_records(since_seconds=24 * 3600)
        assert [record.input_name for record in within_day] == ["recent.ts"]

    def test_none_returns_all(self, temp_history):
        now = time.time()
        history.add_record(_record("recent.ts", now - 3600))
        history.add_record(_record("old.ts", now - 10 * 24 * 3600))
        assert len(history.list_records()) == 2

    def test_sorted_newest_first(self, temp_history):
        now = time.time()
        history.add_record(_record("older.ts", now - 7200))
        history.add_record(_record("newer.ts", now - 60))
        names = [record.input_name for record in history.list_records()]
        assert names == ["newer.ts", "older.ts"]
