"""Generate SVG terminal demo captures for README."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

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

ASSETS = Path(__file__).resolve().parent

_theme = Theme(
    {
        "bar.back": "grey23",
        "bar.complete": "bright_magenta",
        "bar.finished": "bright_green",
    }
)


def banner_demo():
    console = Console(theme=_theme, record=True, width=100)
    banner = Text()
    banner.append("M E D I X", style="bold bright_magenta")
    banner.append("\n")
    banner.append("Media Format Converter", style="italic bright_cyan")
    console.print(
        Panel(
            banner,
            border_style="bright_magenta",
            padding=(1, 4),
            subtitle="[dim]v1.2.0[/dim]",
            subtitle_align="right",
        )
    )
    console.print()
    console.print("  [dim]Scanning[/dim] /Users/demo/Videos")
    console.print("  [dim]Found 4 media file(s)[/dim]\n")
    console.save_svg(str(ASSETS / "demo-banner.svg"), title="medix")


def files_table_demo():
    console = Console(theme=_theme, record=True, width=100)
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

    files = [
        ("1", "VTS_01_1.VOB", "VOB", "720x480", "01:23:45", "1.1 GB"),
        ("2", "VTS_01_2.VOB", "VOB", "720x480", "01:24:02", "1.1 GB"),
        ("3", "VTS_01_3.VOB", "VOB", "720x480", "00:58:30", "823.4 MB"),
        ("4", "vacation_2024.mp4", "MP4", "1920x1080", "00:12:15", "245.7 MB"),
    ]
    for row in files:
        table.add_row(*row)
    table.add_section()
    table.add_row(
        "",
        "[bold]4 file(s)[/bold]",
        "",
        "",
        "[bold]03:58:32[/bold]",
        "[bold]3.2 GB[/bold]",
    )
    console.print(table)
    console.save_svg(str(ASSETS / "demo-files.svg"), title="medix — discovered files")


def settings_demo():
    console = Console(theme=_theme, record=True, width=100)
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

    table.add_row("Files", "4")
    table.add_row("Output Format", "MP4")
    table.add_row("Video Codec", "H.264 (AVC) — Best Compatibility")
    table.add_row("Audio Codec", "AAC — Most Compatible")
    table.add_row("Resolution", "Keep Original")
    table.add_row("Frame Rate", "Keep Original")
    table.add_row("Preset", "Medium")
    table.add_row("CRF", "23")

    console.print(table)
    console.print()
    console.print("  [dim]Output directory:[/dim] /Users/demo/Videos/converted\n")
    console.print("[bold bright_green]?[/bold bright_green] [bold]Start converting 4 file(s)?[/bold] [bright_green]Yes[/bright_green]")
    console.save_svg(str(ASSETS / "demo-settings.svg"), title="medix — conversion plan")


def progress_demo():
    console = Console(theme=_theme, record=True, width=100)
    console.print()

    lines = [
        " [bright_green] OK [/bright_green]  [bold]VTS_01_1.VOB[/bold]      [bright_magenta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bright_magenta] [bright_cyan]100.0%[/bright_cyan] [dim]│[/dim] 0:14:32 [dim]│[/dim] -:--:--",
        " [bright_green] OK [/bright_green]  [bold]VTS_01_2.VOB[/bold]      [bright_magenta]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bright_magenta] [bright_cyan]100.0%[/bright_cyan] [dim]│[/dim] 0:14:45 [dim]│[/dim] -:--:--",
        " [bright_blue]ENC[/bright_blue]  [bold]VTS_01_3.VOB[/bold]      [bright_magenta]━━━━━━━━━━━━━━━━━━━━━━━━━[/bright_magenta][grey23]━━━━━━━━━━━━━━━[/grey23] [bright_cyan] 62.4%[/bright_cyan] [dim]│[/dim] 0:09:08 [dim]│[/dim] 0:05:31",
        "    [bold][bright_yellow]Overall[/bright_yellow][/bold]           [bright_magenta]━━━━━━━━━━━━━━━━━━━━━━━━━━[/bright_magenta][grey23]━━━━━━━━━━━━━━[/grey23] [bright_cyan] 65.6%[/bright_cyan] [dim]│[/dim] 0:38:25 [dim]│[/dim] 0:19:30",
    ]
    for line in lines:
        console.print(line)

    console.save_svg(str(ASSETS / "demo-progress.svg"), title="medix — conversion progress")


def prereq_demo():
    console = Console(theme=_theme, record=True, width=100)
    banner = Text()
    banner.append("M E D I X", style="bold bright_magenta")
    banner.append("\n")
    banner.append("Media Format Converter", style="italic bright_cyan")
    console.print(
        Panel(
            banner,
            border_style="bright_magenta",
            padding=(1, 4),
            subtitle="[dim]v1.2.0[/dim]",
            subtitle_align="right",
        )
    )
    console.print()
    console.print(
        "[bold red]Missing prerequisites:[/bold red] ffmpeg, ffprobe\n"
        "  [dim]System: darwin (arm64)[/dim]"
    )
    console.print()
    console.print("  [bright_cyan]Detected package manager:[/bright_cyan] Homebrew")
    console.print("  [dim]Command: brew install ffmpeg[/dim]\n")
    console.print(
        "[bold bright_green]?[/bold bright_green] [bold]Install ffmpeg via Homebrew?[/bold] [bright_green]Yes[/bright_green]"
    )
    console.print()
    console.print("[bold bright_green]ffmpeg installed successfully![/bold bright_green]\n")
    console.save_svg(str(ASSETS / "demo-prereq.svg"), title="medix — auto-install prerequisites")


def complete_demo():
    console = Console(theme=_theme, record=True, width=100)
    console.print(
        Panel(
            "[bold bright_green]All 4 file(s) converted successfully![/bold bright_green]\n"
            "[dim]Output:[/dim] /Users/demo/Videos/converted",
            border_style="bright_green",
            title="[bold] Complete [/bold]",
            title_align="left",
            padding=(1, 2),
        )
    )
    console.save_svg(str(ASSETS / "demo-complete.svg"), title="medix — complete")


if __name__ == "__main__":
    banner_demo()
    files_table_demo()
    settings_demo()
    progress_demo()
    prereq_demo()
    complete_demo()
    print(f"Generated SVGs in {ASSETS}")
