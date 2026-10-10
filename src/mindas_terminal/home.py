"""Home window: the start screen. Click a shell to open it, or a tool; everything also has a key."""

from __future__ import annotations

import os
import platform
import random

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Grid, Vertical
from textual.screen import Screen
from textual.widgets import Button, Static

from . import __version__
from .shells import Shell

LOGO = r"""
           _           _
 _ __ ___ (_)_ __   __| | __ _ ___
| '_ ` _ \| | '_ \ / _` |/ _` / __|
| | | | | | | | | | (_| | (_| \__ \
|_| |_| |_|_|_| |_|\__,_|\__,_|___/
""".strip("\n")

GRADIENT = ["#7aa2ff", "#8b9cff", "#9c95ff", "#ad8fff", "#b18cff"]

TIPS = [
    "Ctrl+B then % splits side by side; Ctrl+B then \" splits top and bottom.",
    "Scroll with the mouse wheel to enter copy mode; / searches, y copies.",
    "Ctrl+B then g finds a command for your field; it is typed, never run.",
    "Ctrl+B then t shows which process holds your GPU memory (sort with g).",
    "Ctrl+B then z zooms a pane; again to restore the layout.",
    "mindas-terminal --aliases list shows 89 helpers such as mkcd, extract and sq.",
    "In copy mode, V selects whole lines: handy for copying a stack trace.",
    "Ctrl+B then : opens the command palette: themes, profiles, shells, settings.",
    "The task manager's f key shows only what this terminal started.",
    "Every toolkit placeholder is quoted for you, so values with spaces stay one argument.",
    "Clicking the words in the status bar runs them: tab, split, tools, tasks, manual.",
    "Ctrl+B then m opens this manual offline; man pages: mindas-terminal --man.",
]


def system_line() -> str:
    try:
        import psutil

        mem = psutil.virtual_memory()
        hw = f"{psutil.cpu_count() or 1} CPUs, {mem.total / 1024**3:.1f} GB RAM"
    except Exception:  # noqa: BLE001 - information only
        hw = ""
    where = platform.system() + " " + platform.release()
    if "microsoft" in platform.release().lower() or os.environ.get("WSL_DISTRO_NAME"):
        where += f" (WSL: {os.environ.get('WSL_DISTRO_NAME', 'Linux')})"
    return f"{platform.node()}  |  {where}  |  {hw}"


class HomeScreen(Screen[Shell | None]):
    """Dismisses with the shell to open (None: the default shell)."""

    DEFAULT_CSS = """
    HomeScreen { background: $background; align: center middle; }
    #home { width: 96; max-width: 100%; height: auto; }
    #logo { width: auto; margin-top: 1; }
    #tag { width: 100%; text-align: center; color: $text-muted; margin-bottom: 1; }
    .section { width: 100%; color: $accent; text-style: bold; margin: 1 0 0 1; }
    .cards { grid-size: 3; grid-gutter: 0 1; height: auto; padding: 0 1; }
    .cards Button { width: 100%; height: 3; border: round $panel; background: $surface; }
    .cards Button:hover { border: round $accent; }
    .cards Button:focus { border: round $accent; text-style: bold; }
    #sys { width: 100%; text-align: center; color: $text-muted; margin-top: 1; }
    #tip { width: 100%; text-align: center; color: $secondary; margin-top: 1; }
    #keys { width: 100%; text-align: center; color: $text-muted; margin-top: 1; }
    """
    BINDINGS = [
        Binding("enter", "open(0)", "Default shell", show=False),
        Binding("g", "tool('toolkit')", "Toolkits"),
        Binding("t", "tool('task_manager')", "Tasks"),
        Binding("m", "tool('manual')", "Manual"),
        Binding("question_mark", "tool('help')", "Keys"),
        Binding("colon", "tool('command_palette')", "Palette"),
        Binding("q", "tool('quit_app')", "Quit"),
        Binding("escape", "open(0)", "Continue", show=False),
        *[Binding(str(i), f"open({i - 1})", show=False) for i in range(1, 10)],
    ]

    def __init__(self, shells: list[Shell], profile: str | None = None) -> None:
        super().__init__()
        self.shells = shells
        self.profile = profile

    def compose(self) -> ComposeResult:
        with Vertical(id="home"):
            logo = Text()
            for i, line in enumerate(LOGO.splitlines()):
                logo.append(line + "\n", style=f"bold {GRADIENT[min(i, len(GRADIENT) - 1)]}")
            logo.append("                   terminal", style="bold #5eead4")
            with Center():
                yield Static(logo, id="logo")
            yield Static(f"v{__version__}   a universal terminal for Windows and Linux   bash first everywhere",
                         id="tag")
            yield Static("Open a shell  (click, or press its number; Enter for the first)", classes="section")
            with Grid(classes="cards"):
                for i, sh in enumerate(self.shells[:8]):
                    yield Button(f"{i + 1}  {sh.name}", id=f"shell-{i}")
            yield Static("Tools", classes="section")
            with Grid(classes="cards"):
                yield Button("g  Toolkits", id="tool-toolkit")
                yield Button("t  Task manager", id="tool-task_manager")
                yield Button("m  Manual", id="tool-manual")
                yield Button("?  Keyboard", id="tool-help")
                yield Button(":  Command palette", id="tool-command_palette")
                yield Button("q  Quit", id="tool-quit_app")
            field = f"profile: {self.profile}   " if self.profile else ""
            yield Static(system_line(), id="sys")
            yield Static("Tip: " + random.choice(TIPS), id="tip")  # noqa: S311 - not security related
            yield Static(f"{field}: palette   Ctrl+Q quit   Ctrl+B H brings this window back", id="keys")

    def on_mount(self) -> None:
        first = self.query("Button").first()
        if first:
            first.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id or ""
        if bid.startswith("shell-"):
            self.action_open(int(bid.split("-", 1)[1]))
        elif bid.startswith("tool-"):
            self.action_tool(bid.split("-", 1)[1])

    def action_open(self, index: int) -> None:
        if 0 <= index < len(self.shells):
            self.dismiss(self.shells[index])

    def action_tool(self, name: str) -> None:
        getattr(self.app, f"action_{name}")()
