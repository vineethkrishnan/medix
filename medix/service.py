from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Tuple
from xml.sax.saxutils import escape

from .history import config_dir

LAUNCHD_LABEL = "de.vinelabs.medix-gui"
_DETACHED_PROCESS = 0x00000008
_CREATE_NEW_PROCESS_GROUP = 0x00000200


def state_path() -> Path:
    return config_dir() / "gui-daemon.json"


def log_path() -> Path:
    return config_dir() / "gui.log"


def _read_state() -> Optional[dict]:
    path = state_path()
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _write_state(pid: int, host: str, port: int) -> None:
    path = state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"pid": pid, "host": host, "port": port}), encoding="utf-8"
    )


def _clear_state() -> None:
    path = state_path()
    if path.exists():
        path.unlink()


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes

        handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
        if handle:
            ctypes.windll.kernel32.CloseHandle(handle)
            return True
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def _terminate(pid: int) -> None:
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/F", "/PID", str(pid)],
            capture_output=True,
        )
        return
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError:
        pass


def _spawn_kwargs() -> dict:
    if os.name == "posix":
        return {"start_new_session": True}
    return {"creationflags": _DETACHED_PROCESS | _CREATE_NEW_PROCESS_GROUP}


def start_background(host: str, port: int) -> Tuple[str, dict]:
    """Start the GUI server detached. Returns (status, info)."""
    existing = _read_state()
    if existing and _pid_alive(int(existing.get("pid", 0))):
        return "already_running", existing

    log_path().parent.mkdir(parents=True, exist_ok=True)
    args = [
        sys.executable,
        "-m",
        "medix.gui",
        "--host",
        host,
        "--port",
        str(port),
        "--no-browser",
    ]
    with open(log_path(), "ab") as log_file:
        process = subprocess.Popen(
            args,
            stdout=log_file,
            stderr=log_file,
            stdin=subprocess.DEVNULL,
            **_spawn_kwargs(),
        )

    time.sleep(1.0)
    if process.poll() is not None:
        tail = ""
        try:
            tail = "\n".join(log_path().read_text(encoding="utf-8").splitlines()[-5:])
        except OSError:
            pass
        return "failed", {"log": tail}

    info = {"pid": process.pid, "host": host, "port": port}
    _write_state(process.pid, host, port)
    return "started", info


def stop_background() -> Tuple[str, Optional[dict]]:
    state = _read_state()
    if not state or not _pid_alive(int(state.get("pid", 0))):
        _clear_state()
        return "not_running", None

    pid = int(state["pid"])
    _terminate(pid)
    for _ in range(50):
        if not _pid_alive(pid):
            break
        time.sleep(0.1)
    _clear_state()
    return "stopped", state


def status_background() -> Tuple[str, Optional[dict]]:
    state = _read_state()
    if state and _pid_alive(int(state.get("pid", 0))):
        return "running", state
    return "stopped", None


# ──────────────────────────────────────────────────────────── launchd service


def launchd_plist_path() -> Path:
    return Path.home() / "Library" / "LaunchAgents" / f"{LAUNCHD_LABEL}.plist"


def build_launchd_plist(host: str, port: int) -> str:
    program_args = [
        sys.executable,
        "-m",
        "medix.gui",
        "--host",
        host,
        "--port",
        str(port),
        "--no-browser",
    ]
    args_xml = "\n".join(f"    <string>{escape(arg)}</string>" for arg in program_args)
    log = escape(str(log_path()))
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>{LAUNCHD_LABEL}</string>
  <key>ProgramArguments</key>
  <array>
{args_xml}
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>{log}</string>
  <key>StandardErrorPath</key>
  <string>{log}</string>
</dict>
</plist>
"""


def install_service(host: str, port: int) -> Tuple[bool, str]:
    if sys.platform != "darwin":
        return False, "Service install is only supported on macOS (launchd)."

    plist = launchd_plist_path()
    plist.parent.mkdir(parents=True, exist_ok=True)
    log_path().parent.mkdir(parents=True, exist_ok=True)
    plist.write_text(build_launchd_plist(host, port), encoding="utf-8")

    subprocess.run(["launchctl", "unload", str(plist)], capture_output=True)
    result = subprocess.run(
        ["launchctl", "load", "-w", str(plist)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return False, (result.stderr or result.stdout).strip()
    return True, str(plist)


def uninstall_service() -> Tuple[bool, str]:
    if sys.platform != "darwin":
        return False, "Service install is only supported on macOS (launchd)."

    plist = launchd_plist_path()
    if not plist.exists():
        return False, "No installed service found."

    subprocess.run(["launchctl", "unload", "-w", str(plist)], capture_output=True)
    plist.unlink()
    return True, str(plist)
