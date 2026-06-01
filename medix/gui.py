from __future__ import annotations

import json
import queue
import shutil
import subprocess
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import parse_qs, urlparse

import click

from . import __version__, service
from .cli import _resolve_output_path, discover_files
from .converter import ConvertSettings, convert_file, probe_file
from .dependencies import (
    find_missing_tools,
    get_manual_install_hint,
)
from .formats import (
    AUDIO_BITRATES,
    AUDIO_CODECS,
    FRAME_RATES,
    MEDIA_EXTENSIONS,
    OUTPUT_FORMATS,
    PRESETS,
    RESOLUTIONS,
    VIDEO_CODECS,
)
from .history import HistoryRecord, add_record, list_records

WEB_DIR = Path(__file__).parent / "web"

DURATION_WINDOWS = {
    "24h": 24 * 3600,
    "7d": 7 * 24 * 3600,
    "30d": 30 * 24 * 3600,
    "all": None,
}

_CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".svg": "image/svg+xml",
}

_STATIC_PATHS = {name: WEB_DIR / name for name in ("index.html", "style.css", "app.js")}


# ──────────────────────────────────────────────────────────── job tracking


class Job:
    def __init__(self, job_id: str) -> None:
        self.id = job_id
        self._lock = threading.Lock()
        self._subscribers: List[queue.Queue] = []
        self._latest: Optional[dict] = None
        self.done = False

    def publish(self, snapshot: dict) -> None:
        with self._lock:
            self._latest = snapshot
            if snapshot.get("done"):
                self.done = True
            subscribers = list(self._subscribers)
        for subscriber in subscribers:
            subscriber.put(snapshot)

    def subscribe(self) -> queue.Queue:
        subscriber: queue.Queue = queue.Queue()
        with self._lock:
            if self._latest is not None:
                subscriber.put(self._latest)
            self._subscribers.append(subscriber)
        return subscriber

    def unsubscribe(self, subscriber: queue.Queue) -> None:
        with self._lock:
            if subscriber in self._subscribers:
                self._subscribers.remove(subscriber)


_jobs: Dict[str, Job] = {}
_jobs_lock = threading.Lock()
_job_counter = 0


def _new_job() -> Job:
    global _job_counter
    with _jobs_lock:
        _job_counter += 1
        job = Job(f"job-{_job_counter}")
        _jobs[job.id] = job
    return job


def _get_job(job_id: str) -> Optional[Job]:
    with _jobs_lock:
        return _jobs.get(job_id)


# ──────────────────────────────────────────────────────────── conversion run


def _run_job(
    job: Job,
    input_paths: List[Path],
    settings: ConvertSettings,
    output_dir: Path,
    input_root: Path,
    recursive: bool,
) -> None:
    fmt_def = OUTPUT_FORMATS[settings.output_format]
    output_dir.mkdir(parents=True, exist_ok=True)

    files = [
        {
            "name": path.name,
            "input": str(path),
            "output": "",
            "status": "queued",
            "pct": 0.0,
        }
        for path in input_paths
    ]

    def snapshot(done: bool = False, summary: Optional[dict] = None) -> dict:
        overall = sum(item["pct"] for item in files) / len(files) if files else 1.0
        return {
            "files": [dict(item) for item in files],
            "overall": overall,
            "done": done,
            "summary": summary,
        }

    job.publish(snapshot())

    succeeded = 0
    failed = 0

    for index, input_path in enumerate(input_paths):
        info = probe_file(input_path)
        if info is None:
            files[index]["status"] = "failed"
            files[index]["error"] = "Could not read media file."
            failed += 1
            job.publish(snapshot())
            continue

        out_file = _resolve_output_path(
            info, fmt_def, output_dir, input_root, recursive
        )
        files[index]["output"] = str(out_file)
        files[index]["status"] = "encoding"
        job.publish(snapshot())

        last_published_pct = -1.0

        def on_progress(pct: float, idx: int = index) -> None:
            nonlocal last_published_pct
            files[idx]["pct"] = pct
            whole = round(pct * 100)
            if whole != last_published_pct:
                last_published_pct = whole
                job.publish(snapshot())

        started = time.time()
        ok, error = convert_file(
            info.path,
            out_file,
            settings,
            total_duration=info.duration,
            on_progress=on_progress,
        )
        elapsed = time.time() - started

        files[index]["pct"] = 1.0
        output_size = out_file.stat().st_size if ok and out_file.exists() else 0

        if ok:
            files[index]["status"] = "done"
            succeeded += 1
        else:
            files[index]["status"] = "failed"
            files[index]["error"] = error
            failed += 1

        add_record(
            HistoryRecord(
                timestamp=time.time(),
                input_name=info.path.name,
                input_path=str(info.path),
                output_path=str(out_file),
                output_format=settings.output_format,
                video_codec=settings.video_codec,
                audio_codec=settings.audio_codec,
                media_duration=info.duration,
                input_size=info.size,
                output_size=output_size,
                elapsed=elapsed,
                status="success" if ok else "failed",
                error="" if ok else error,
            )
        )
        job.publish(snapshot())

    summary = {
        "succeeded": succeeded,
        "failed": failed,
        "output_dir": str(output_dir),
    }
    job.publish(snapshot(done=True, summary=summary))


# ──────────────────────────────────────────────────────────── native dialogs

_TK_SNIPPET = """
import sys
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()
root.attributes("-topmost", True)
mode = sys.argv[1] if len(sys.argv) > 1 else "file"
if mode == "dir":
    chosen = filedialog.askdirectory(title="Select folder")
else:
    chosen = filedialog.askopenfilename(title="Select media file")
sys.stdout.write(chosen or "")
"""


def _run_picker(cmd: list) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    return result.stdout.strip()


def _pick_macos(mode: str) -> str:
    prompt = "Select folder" if mode == "dir" else "Select media file"
    chooser = "choose folder" if mode == "dir" else "choose file"
    script = f'POSIX path of ({chooser} with prompt "{prompt}")'
    return _run_picker(["osascript", "-e", script])


def _pick_windows(mode: str) -> str:
    if mode == "dir":
        script = (
            "Add-Type -AssemblyName System.Windows.Forms;"
            "$d = New-Object System.Windows.Forms.FolderBrowserDialog;"
            "if ($d.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK)"
            " { [Console]::Out.Write($d.SelectedPath) }"
        )
    else:
        script = (
            "Add-Type -AssemblyName System.Windows.Forms;"
            "$f = New-Object System.Windows.Forms.OpenFileDialog;"
            "$f.Title = 'Select media file';"
            "if ($f.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK)"
            " { [Console]::Out.Write($f.FileName) }"
        )
    return _run_picker(["powershell", "-NoProfile", "-STA", "-Command", script])


def _pick_linux(mode: str) -> str:
    if shutil.which("zenity"):
        cmd = ["zenity", "--file-selection"]
        if mode == "dir":
            cmd.append("--directory")
        return _run_picker(cmd)
    if shutil.which("kdialog"):
        flag = "--getexistingdirectory" if mode == "dir" else "--getopenfilename"
        return _run_picker(["kdialog", flag])
    return _run_picker([sys.executable, "-c", _TK_SNIPPET, mode])


def _native_pick(mode: str) -> str:
    try:
        if sys.platform == "darwin":
            return _pick_macos(mode)
        if sys.platform.startswith("win"):
            return _pick_windows(mode)
        return _pick_linux(mode)
    except (subprocess.SubprocessError, OSError):
        return ""


def _broken_tools() -> List[str]:
    """Tools that are on PATH but crash when run (e.g. a broken FFmpeg build)."""
    broken = []
    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool) is None:
            continue
        try:
            result = subprocess.run([tool, "-version"], capture_output=True, timeout=10)
            if result.returncode != 0:
                broken.append(tool)
        except (subprocess.SubprocessError, OSError):
            broken.append(tool)
    return broken


def _open_in_file_manager(target: Path) -> bool:
    if not target.exists():
        return False
    try:
        if sys.platform == "darwin":
            subprocess.Popen(["open", str(target)])
        elif sys.platform.startswith("win"):
            subprocess.Popen(["explorer", str(target)])
        else:
            subprocess.Popen(["xdg-open", str(target)])
        return True
    except OSError:
        return False


# ──────────────────────────────────────────────────────────── request handler


class MedixHandler(BaseHTTPRequestHandler):
    server_version = f"medix-gui/{__version__}"

    def log_message(self, *args) -> None:  # noqa: D401 - silence default logging
        pass

    # ---- helpers ----

    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _is_local_origin(self) -> bool:
        host = self.headers.get("Host", "").rsplit(":", 1)[0].strip("[]")
        if host not in ("127.0.0.1", "localhost", "::1"):
            return False
        origin = self.headers.get("Origin")
        if origin:
            hostname = urlparse(origin).hostname
            if hostname not in ("127.0.0.1", "localhost", "::1"):
                return False
        return True

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            parsed = json.loads(raw.decode("utf-8"))
            return parsed if isinstance(parsed, dict) else {}
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}

    def _serve_static(self, path: str) -> None:
        name = "index.html" if path in ("", "/") else path.lstrip("/")
        target = _STATIC_PATHS.get(name)
        if target is None or not target.is_file():
            self.send_error(404)
            return
        body = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", _CONTENT_TYPES[target.suffix])
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # ---- routing ----

    def do_GET(self) -> None:
        if not self._is_local_origin():
            self.send_error(403)
            return

        parsed = urlparse(self.path)
        route = parsed.path

        if route == "/api/prereq":
            self._handle_prereq()
        elif route == "/api/formats":
            self._handle_formats()
        elif route == "/api/history":
            self._handle_history(parse_qs(parsed.query))
        elif route == "/api/progress":
            self._handle_progress(parse_qs(parsed.query))
        else:
            self._serve_static(route)

    def do_POST(self) -> None:
        if not self._is_local_origin():
            self.send_error(403)
            return

        if "application/json" not in self.headers.get("Content-Type", ""):
            self.send_error(415)
            return

        route = urlparse(self.path).path
        if route == "/api/scan":
            self._handle_scan()
        elif route == "/api/convert":
            self._handle_convert()
        elif route == "/api/pick":
            self._handle_pick()
        elif route == "/api/open":
            self._handle_open()
        else:
            self.send_error(404)

    # ---- endpoint handlers ----

    def _handle_prereq(self) -> None:
        missing = [tool.name for tool in find_missing_tools()]
        broken = _broken_tools() if not missing else []
        hint = ""
        if missing:
            hint = get_manual_install_hint()
        elif broken:
            hint = (
                "FFmpeg is installed but fails to run. Reinstall it "
                "(on macOS: brew reinstall ffmpeg)."
            )
        self._send_json(
            {
                "ready": not missing and not broken,
                "missing": missing,
                "broken": broken,
                "hint": hint,
            }
        )

    def _handle_formats(self) -> None:
        self._send_json(
            {
                "output_formats": OUTPUT_FORMATS,
                "video_codecs": VIDEO_CODECS,
                "audio_codecs": AUDIO_CODECS,
                "resolutions": RESOLUTIONS,
                "presets": PRESETS,
                "frame_rates": FRAME_RATES,
                "audio_bitrates": AUDIO_BITRATES,
                "extensions": sorted(MEDIA_EXTENSIONS),
            }
        )

    def _handle_history(self, query: Dict[str, List[str]]) -> None:
        window = (query.get("since") or ["7d"])[0]
        since_seconds = DURATION_WINDOWS.get(window, DURATION_WINDOWS["7d"])
        records = list_records(since_seconds)
        self._send_json(
            {
                "window": window,
                "records": [record.__dict__ for record in records],
            }
        )

    def _handle_scan(self) -> None:
        body = self._read_body()
        raw_path = (body.get("path") or "").strip()
        recursive = bool(body.get("recursive"))
        if not raw_path:
            self._send_json({"error": "No path provided."}, status=400)
            return

        root = Path(raw_path).expanduser()
        if not root.exists():
            self._send_json({"error": f"Path not found: {raw_path}"}, status=400)
            return

        files = discover_files(root.resolve(), recursive)
        results = []
        for path in files:
            info = probe_file(path)
            if info is None:
                continue
            results.append(
                {
                    "name": info.path.name,
                    "path": str(info.path),
                    "type": info.path.suffix.upper().lstrip("."),
                    "resolution": info.resolution or "N/A",
                    "duration": info.duration,
                    "size": info.size,
                    "video_codec": info.video_codec,
                    "audio_codec": info.audio_codec,
                }
            )

        if files and not results:
            self._send_json(
                {
                    "error": (
                        f"Found {len(files)} media file(s) but could not read any "
                        "with ffprobe. FFmpeg/ffprobe may be broken "
                        "(on macOS: brew reinstall ffmpeg)."
                    )
                },
                status=400,
            )
            return

        default_output = (
            root / "converted" if root.is_dir() else root.parent / "converted"
        )
        self._send_json(
            {
                "root": str(root.resolve()),
                "is_dir": root.is_dir(),
                "recursive": recursive,
                "files": results,
                "default_output": str(default_output),
            }
        )

    def _handle_convert(self) -> None:
        body = self._read_body()
        raw_files = body.get("files") or []
        raw_settings = body.get("settings") or {}
        input_root = (body.get("input_root") or "").strip()
        recursive = bool(body.get("recursive"))
        output_dir = (body.get("output_dir") or "").strip()

        input_paths = [Path(item) for item in raw_files if item]
        input_paths = [path for path in input_paths if path.exists()]
        if not input_paths:
            self._send_json({"error": "No valid files to convert."}, status=400)
            return

        output_format = raw_settings.get("output_format", "MP4")
        if output_format not in OUTPUT_FORMATS:
            self._send_json({"error": "Unknown output format."}, status=400)
            return

        fmt_def = OUTPUT_FORMATS[output_format]
        settings = ConvertSettings(
            output_format=output_format,
            video_codec=raw_settings.get("video_codec", fmt_def["default_vcodec"]),
            audio_codec=raw_settings.get("audio_codec", fmt_def["default_acodec"]),
            resolution=raw_settings.get("resolution", "original"),
            preset=raw_settings.get("preset", "medium"),
            crf=int(raw_settings.get("crf", 23)),
            frame_rate=raw_settings.get("frame_rate", "original"),
            audio_bitrate=raw_settings.get("audio_bitrate", "auto"),
        )

        root = (
            Path(input_root).expanduser().resolve()
            if input_root
            else (input_paths[0].parent)
        )
        out_dir = (
            Path(output_dir).expanduser().resolve()
            if output_dir
            else root / "converted"
            if root.is_dir()
            else root.parent / "converted"
        )

        job = _new_job()
        worker = threading.Thread(
            target=_run_job,
            args=(job, input_paths, settings, out_dir, root, recursive),
            daemon=True,
        )
        worker.start()
        self._send_json({"job_id": job.id})

    def _handle_progress(self, query: Dict[str, List[str]]) -> None:
        job_id = (query.get("job") or [""])[0]
        job = _get_job(job_id)
        if job is None:
            self.send_error(404)
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        subscriber = job.subscribe()
        try:
            while True:
                try:
                    snapshot = subscriber.get(timeout=15)
                except queue.Empty:
                    self.wfile.write(b": ping\n\n")
                    self.wfile.flush()
                    continue
                payload = json.dumps(snapshot).encode("utf-8")
                self.wfile.write(b"data: " + payload + b"\n\n")
                self.wfile.flush()
                if snapshot.get("done"):
                    break
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            job.unsubscribe(subscriber)

    def _handle_pick(self) -> None:
        body = self._read_body()
        mode = "dir" if body.get("mode") == "dir" else "file"
        self._send_json({"path": _native_pick(mode)})

    def _handle_open(self) -> None:
        body = self._read_body()
        raw = (body.get("path") or "").strip()
        if not raw:
            self._send_json({"ok": False}, status=400)
            return
        target = Path(raw).expanduser()
        opened = _open_in_file_manager(target)
        self._send_json({"ok": opened})


# ──────────────────────────────────────────────────────────── entry point


def _serve(host: str, port: int, no_browser: bool) -> None:
    server = ThreadingHTTPServer((host, port), MedixHandler)
    url = f"http://{host}:{port}/"

    click.secho("\n  M E D I X  ", fg="magenta", bold=True, nl=False)
    click.secho("local GUI", fg="cyan")
    click.echo(f"  Serving at {url}")
    click.echo("  Press Ctrl+C to stop.\n")

    if not no_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        click.echo("\n  Stopped.")
    finally:
        server.server_close()


@click.group(
    invoke_without_command=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.option("--host", default="127.0.0.1", help="Host to bind.")
@click.option("--port", default=8756, type=int, help="Port to bind.")
@click.option("--no-browser", is_flag=True, help="Do not open the browser.")
@click.version_option(__version__, prog_name="medix-gui")
@click.pass_context
def main(ctx: click.Context, host: str, port: int, no_browser: bool) -> None:
    """Medix local web GUI. Run without a command to serve in the foreground."""
    ctx.obj = {"host": host, "port": port}
    if ctx.invoked_subcommand is None:
        _serve(host, port, no_browser)


@main.command()
@click.pass_context
def start(ctx: click.Context) -> None:
    """Start the GUI as a background process."""
    host, port = ctx.obj["host"], ctx.obj["port"]
    result, info = service.start_background(host, port)
    if result == "already_running":
        click.echo(f"Already running (pid {info['pid']}) on port {info['port']}.")
    elif result == "failed":
        click.secho("Failed to start.", fg="red")
        if info.get("log"):
            click.echo(info["log"])
        ctx.exit(1)
    else:
        click.secho(f"Started (pid {info['pid']}) at http://{host}:{port}/", fg="green")


@main.command()
def stop() -> None:
    """Stop the background GUI process."""
    result, info = service.stop_background()
    if result == "not_running":
        click.echo("Not running.")
    else:
        click.secho(f"Stopped (pid {info['pid']}).", fg="yellow")


@main.command()
def status() -> None:
    """Show whether the background GUI is running."""
    result, info = service.status_background()
    if result == "running":
        click.secho(
            f"Running (pid {info['pid']}) on http://{info['host']}:{info['port']}/",
            fg="green",
        )
    else:
        click.echo("Not running.")


@main.command(name="install-service")
@click.pass_context
def install_service(ctx: click.Context) -> None:
    """Install a launchd service so the GUI auto-starts at login (macOS)."""
    host, port = ctx.obj["host"], ctx.obj["port"]
    ok, detail = service.install_service(host, port)
    if ok:
        click.secho(f"Service installed and loaded: {detail}", fg="green")
        click.echo(f"Auto-starts at login, serving http://{host}:{port}/")
    else:
        click.secho(f"Could not install service: {detail}", fg="red")
        ctx.exit(1)


@main.command(name="uninstall-service")
@click.pass_context
def uninstall_service(ctx: click.Context) -> None:
    """Remove the launchd service (macOS)."""
    ok, detail = service.uninstall_service()
    if ok:
        click.secho(f"Service removed: {detail}", fg="yellow")
    else:
        click.echo(detail)
        ctx.exit(1)


if __name__ == "__main__":
    main()
