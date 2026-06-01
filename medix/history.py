from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional

HISTORY_FILENAME = "history.json"
MAX_RECORDS = 1000


@dataclass
class HistoryRecord:
    timestamp: float
    input_name: str
    input_path: str
    output_path: str
    output_format: str
    video_codec: str
    audio_codec: str
    media_duration: float
    input_size: int
    output_size: int
    elapsed: float
    status: str
    error: str = ""


def config_dir() -> Path:
    override = os.environ.get("MEDIX_CONFIG_DIR")
    if override:
        return Path(override)

    if os.name == "nt":
        base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        return Path(base) / "medix"

    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else Path.home() / ".config"
    return base / "medix"


def history_path() -> Path:
    return config_dir() / HISTORY_FILENAME


def _read_all() -> List[HistoryRecord]:
    path = history_path()
    if not path.exists():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    if not isinstance(raw, list):
        return []

    records: List[HistoryRecord] = []
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        try:
            records.append(HistoryRecord(**entry))
        except TypeError:
            continue
    return records


def _write_all(records: List[HistoryRecord]) -> None:
    path = history_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [asdict(record) for record in records[-MAX_RECORDS:]]
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp.replace(path)


def add_record(record: HistoryRecord) -> None:
    records = _read_all()
    records.append(record)
    _write_all(records)


def list_records(since_seconds: Optional[float] = None) -> List[HistoryRecord]:
    records = _read_all()
    if since_seconds is not None:
        cutoff = time.time() - since_seconds
        records = [record for record in records if record.timestamp >= cutoff]
    return sorted(records, key=lambda record: record.timestamp, reverse=True)


def clear() -> None:
    path = history_path()
    if path.exists():
        path.unlink()
