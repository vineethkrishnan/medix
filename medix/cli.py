from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import click
import questionary
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from .converter import (
    ConvertSettings,
    MediaInfo,
    check_ffmpeg,
    convert_file,
    probe_file,
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

# ──────────────────────────────────────────────────────────────── styling

PROMPT_STYLE = questionary.Style(
    [
        ("qmark", "fg:ansibrightmagenta bold"),
        ("question", "fg:ansiwhite bold"),
        ("answer", "fg:ansibrightgreen bold"),
        ("pointer", "fg:ansibrightmagenta bold"),
        ("highlighted", "fg:ansibrightmagenta bold"),
        ("selected", "fg:ansibrightgreen"),
        ("instruction", "fg:ansibrightcyan"),
    ]
)

_theme = Theme(
    {
        "bar.back": "grey23",
        "bar.complete": "bright_magenta",
        "bar.finished": "bright_green",
    }
)

console = Console(theme=_theme)


# ──────────────────────────────────────────────────────────── ui helpers


def display_banner() -> None:
    banner = Text()
    banner.append("M E D I X", style="bold bright_magenta")
    banner.append("\n")
    banner.append("Media Format Converter", style="italic bright_cyan")
    console.print(
        Panel(
            banner,
            border_style="bright_magenta",
            padding=(1, 4),
            subtitle="[dim]v1.0.0[/dim]",
            subtitle_align="right",
        )
    )
    console.print()


def _fmt_duration(seconds: float) -> str:
    if seconds <= 0:
        return "--:--"
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def _fmt_size(n: int) -> str:
    if n <= 0:
        return "N/A"
    v = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if v < 1024:
            return f"{v:.1f} {unit}"
        v /= 1024
    return f"{v:.1f} PB"


# ──────────────────────────────────────────────────────── file discovery


def discover_files(path: Path, recursive: bool = False) -> List[Path]:
    if path.is_file():
        return [path] if path.suffix.lower() in MEDIA_EXTENSIONS else []
    iterator = path.rglob("*") if recursive else path.iterdir()
    return sorted(
        p for p in iterator if p.is_file() and p.suffix.lower() in MEDIA_EXTENSIONS
    )


def display_files_table(files_info: List[MediaInfo]) -> None:
    table = Table(
        box=box.ROUNDED,
        border_style="bright_cyan",
        header_style="bold bright_white on grey11",
        title=" Discovered Media Files ",
        title_style="bold bright_cyan",
        row_styles=["", "dim"],
    )
    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("File", style="bright_white", max_width=45, no_wrap=True)
    table.add_column("Type", style="yellow", width=6, justify="center")
    table.add_column("Resolution", style="green", width=12, justify="center")
    table.add_column("Duration", style="cyan", width=10, justify="center")
    table.add_column("Size", style="magenta", width=10, justify="right")

    total_dur = 0.0
    total_size = 0
    for i, info in enumerate(files_info, 1):
        table.add_row(
            str(i),
            info.path.name,
            info.path.suffix.upper().lstrip("."),
            info.resolution or "N/A",
            _fmt_duration(info.duration),
            _fmt_size(info.size),
        )
        total_dur += info.duration
        total_size += info.size

    table.add_section()
    table.add_row(
        "",
        f"[bold]{len(files_info)} file(s)[/bold]",
        "",
        "",
        f"[bold]{_fmt_duration(total_dur)}[/bold]",
        f"[bold]{_fmt_size(total_size)}[/bold]",
    )
    console.print(table)
    console.print()


# ─────────────────────────────────────────────── interactive selection


def _abort() -> None:
    console.print("\n[red]Aborted.[/red]")
    sys.exit(1)


def _select(message: str, options: Dict[str, str], default: Optional[str] = None) -> str:
    choices = [
        questionary.Choice(title=f"{k:16s} {v}", value=k) for k, v in options.items()
    ]
    result = questionary.select(
        message, choices=choices, style=PROMPT_STYLE, default=default,
    ).ask()
    if result is None:
        _abort()
    return result


def select_source_formats(files: List[Path]) -> List[Path]:
    counts: Dict[str, int] = {}
    for f in files:
        ext = f.suffix.lower()
        counts[ext] = counts.get(ext, 0) + 1
    if len(counts) <= 1:
        return files

    choices = [
        questionary.Choice(
            title=f"{ext.upper().lstrip('.')} ({n} file{'s' if n > 1 else ''})",
            value=ext,
            checked=True,
        )
        for ext, n in sorted(counts.items())
    ]

    while True:
        selected = questionary.checkbox(
            "Multiple formats found \u2014 select which to convert:",
            choices=choices,
            style=PROMPT_STYLE,
        ).ask()
        if selected is None:
            _abort()
        if selected:
            break
        console.print("[red]Select at least one format.[/red]")

    return [f for f in files if f.suffix.lower() in selected]


def select_output_format() -> str:
    choices = [
        questionary.Choice(
            title=f"{name:6s} {fmt['description']}", value=name,
        )
        for name, fmt in OUTPUT_FORMATS.items()
    ]
    result = questionary.select(
        "Output format:", choices=choices, style=PROMPT_STYLE,
    ).ask()
    if result is None:
        _abort()
    return result


def configure_settings(format_name: str) -> ConvertSettings:
    fmt = OUTPUT_FORMATS[format_name]
    settings = ConvertSettings(
        output_format=format_name,
        video_codec=fmt["default_vcodec"],
        audio_codec=fmt["default_acodec"],
    )

    want_advanced = questionary.confirm(
        "Configure advanced settings?", default=False, style=PROMPT_STYLE,
    ).ask()
    if want_advanced is None:
        _abort()
    if not want_advanced:
        return settings

    console.print()
    console.print(
        Panel(
            "[bold bright_white]Advanced Encoding Settings[/bold bright_white]",
            border_style="bright_cyan",
            padding=(0, 2),
        )
    )

    vcodec = _select("Video codec:", VIDEO_CODECS, default=settings.video_codec)
    settings.video_codec = vcodec

    acodec = _select("Audio codec:", AUDIO_CODECS, default=settings.audio_codec)
    settings.audio_codec = acodec

    if vcodec != "copy":
        settings.resolution = _select("Resolution:", RESOLUTIONS)
        settings.frame_rate = _select("Frame rate:", FRAME_RATES)

        if vcodec in ("libx264", "libx265"):
            settings.preset = _select("Encoding preset:", PRESETS, default="medium")

            crf = questionary.text(
                "CRF quality (0\u201351, lower = better):",
                default="23",
                style=PROMPT_STYLE,
                validate=lambda x: (
                    True
                    if x.isdigit() and 0 <= int(x) <= 51
                    else "Enter a number between 0 and 51"
                ),
            ).ask()
            if crf is None:
                _abort()
            settings.crf = int(crf)

    if acodec != "copy":
        settings.audio_bitrate = _select("Audio bitrate:", AUDIO_BITRATES)

    return settings


def display_settings_summary(settings: ConvertSettings, file_count: int) -> None:
    table = Table(
        box=box.SIMPLE_HEAVY,
        border_style="bright_yellow",
        title=" Conversion Plan ",
        title_style="bold bright_yellow",
        show_header=False,
        padding=(0, 2),
    )
    table.add_column("Setting", style="bright_white bold")
    table.add_column("Value", style="bright_green")

    table.add_row("Files", str(file_count))
    table.add_row("Output Format", settings.output_format)
    table.add_row(
        "Video Codec", VIDEO_CODECS.get(settings.video_codec, settings.video_codec),
    )
    table.add_row(
        "Audio Codec", AUDIO_CODECS.get(settings.audio_codec, settings.audio_codec),
    )

    if settings.video_codec != "copy":
        table.add_row(
            "Resolution", RESOLUTIONS.get(settings.resolution, settings.resolution),
        )
        table.add_row(
            "Frame Rate", FRAME_RATES.get(settings.frame_rate, settings.frame_rate),
        )
        if settings.video_codec in ("libx264", "libx265"):
            table.add_row("Preset", settings.preset.title())
            table.add_row("CRF", str(settings.crf))

    if settings.audio_codec != "copy":
        table.add_row(
            "Audio Bitrate",
            AUDIO_BITRATES.get(settings.audio_bitrate, settings.audio_bitrate),
        )

    console.print(table)
    console.print()


# ───────────────────────────────────────────────────────── main command


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("path", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), default=None, help="Output directory.")
@click.option("-r", "--recursive", is_flag=True, help="Recurse into subdirectories.")
@click.version_option("1.0.0", prog_name="medix")
def main(path: str, output: Optional[str], recursive: bool) -> None:
    """Medix - Convert media files between formats with style."""
    try:
        _run(path, output, recursive)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted.[/yellow]")
        sys.exit(130)


def _run(path: str, output: Optional[str], recursive: bool) -> None:
    display_banner()

    if not check_ffmpeg():
        console.print(
            "[bold red]Error:[/bold red] ffmpeg and ffprobe must be installed and in PATH."
        )
        console.print("[dim]Install: https://ffmpeg.org/download.html[/dim]")
        sys.exit(1)

    input_path = Path(path).resolve()

    # ── discover ──────────────────────────────────────────────────────

    suffix = "/**" if recursive else ""
    console.print(f"  [dim]Scanning[/dim] {input_path}{suffix}")
    files = discover_files(input_path, recursive)

    if not files:
        console.print("[bold red]No media files found.[/bold red]")
        sys.exit(1)

    console.print(f"  [dim]Found {len(files)} media file(s)[/dim]\n")

    # ── source format filter ──────────────────────────────────────────

    files = select_source_formats(files)
    if not files:
        console.print("[bold red]No files selected.[/bold red]")
        sys.exit(1)

    # ── probe ─────────────────────────────────────────────────────────

    files_info: List[MediaInfo] = []
    with Progress(
        SpinnerColumn(style="bright_magenta"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=30),
        TaskProgressColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Analyzing files\u2026", total=len(files))
        for f in files:
            info = probe_file(f)
            if info:
                files_info.append(info)
            progress.advance(task)

    if not files_info:
        console.print("[bold red]Could not read any media files.[/bold red]")
        sys.exit(1)

    display_files_table(files_info)

    # ── interactive selection ─────────────────────────────────────────

    format_name = select_output_format()
    settings = configure_settings(format_name)
    fmt_def = OUTPUT_FORMATS[format_name]

    # ── output dir ────────────────────────────────────────────────────

    if output:
        output_dir = Path(output).resolve()
    elif input_path.is_dir():
        output_dir = input_path / "converted"
    else:
        output_dir = input_path.parent / "converted"

    settings.output_dir = str(output_dir)

    # ── summary + confirm ─────────────────────────────────────────────

    display_settings_summary(settings, len(files_info))
    console.print(f"  [dim]Output directory:[/dim] {output_dir}\n")

    confirm = questionary.confirm(
        f"Start converting {len(files_info)} file(s)?",
        default=True,
        style=PROMPT_STYLE,
    ).ask()
    if not confirm:
        console.print("[yellow]Cancelled.[/yellow]")
        sys.exit(0)

    output_dir.mkdir(parents=True, exist_ok=True)
    console.print()

    # ── convert ───────────────────────────────────────────────────────

    succeeded = 0
    failed = 0
    errors: List[Tuple[str, str]] = []

    with Progress(
        SpinnerColumn(style="bright_magenta"),
        TextColumn("{task.fields[status]}", justify="left"),
        TextColumn("{task.fields[filename]}", justify="left", style="bold"),
        BarColumn(
            bar_width=40,
            style="bar.back",
            complete_style="bar.complete",
            finished_style="bar.finished",
        ),
        TextColumn("{task.percentage:>5.1f}%", style="bright_cyan"),
        TextColumn("[dim]\u2502[/dim]"),
        TimeElapsedColumn(),
        TextColumn("[dim]\u2502[/dim]"),
        TimeRemainingColumn(),
        console=console,
    ) as progress:

        overall_task = progress.add_task(
            "",
            total=len(files_info),
            filename="[bright_yellow]Overall[/bright_yellow]",
            status="   ",
        )

        for info in files_info:
            # Resolve output path
            if recursive and input_path.is_dir():
                rel = info.path.relative_to(input_path)
                out_file = (output_dir / rel).with_suffix(fmt_def["extension"])
                out_file.parent.mkdir(parents=True, exist_ok=True)
            else:
                out_file = output_dir / (info.path.stem + fmt_def["extension"])

            # Avoid overwriting
            counter = 1
            base_stem = out_file.stem
            while out_file.exists():
                out_file = out_file.with_name(
                    f"{base_stem}_{counter}{fmt_def['extension']}"
                )
                counter += 1

            file_task = progress.add_task(
                "",
                total=1000,
                filename=info.path.name,
                status="[bright_blue]ENC[/bright_blue]",
            )

            def _on_progress(pct: float, tid: int = file_task) -> None:
                progress.update(tid, completed=int(pct * 1000))

            ok, err_msg = convert_file(
                info.path,
                out_file,
                settings,
                total_duration=info.duration,
                on_progress=_on_progress,
            )

            progress.update(file_task, completed=1000)

            if ok:
                progress.update(
                    file_task, status="[bright_green] OK [/bright_green]",
                )
                succeeded += 1
            else:
                progress.update(
                    file_task, status="[bright_red]FAIL[/bright_red]",
                )
                errors.append((info.path.name, err_msg))
                failed += 1

            progress.advance(overall_task)

    # ── report ────────────────────────────────────────────────────────

    console.print()
    if failed == 0:
        console.print(
            Panel(
                f"[bold bright_green]All {succeeded} file(s) converted successfully![/bold bright_green]\n"
                f"[dim]Output:[/dim] {output_dir}",
                border_style="bright_green",
                title="[bold] Complete [/bold]",
                title_align="left",
                padding=(1, 2),
            )
        )
    else:
        msg = (
            f"[bright_green]{succeeded} succeeded[/bright_green]  "
            f"[bright_red]{failed} failed[/bright_red]\n"
            f"[dim]Output:[/dim] {output_dir}"
        )
        if errors:
            msg += "\n\n[bold bright_red]Errors:[/bold bright_red]"
            for name, err in errors:
                short = err[:200] if err else "Unknown error"
                msg += f"\n  [bright_red]\u2022 {name}:[/bright_red] {short}"
        console.print(
            Panel(
                msg,
                border_style="bright_yellow",
                title="[bold] Complete [/bold]",
                title_align="left",
                padding=(1, 2),
            )
        )
