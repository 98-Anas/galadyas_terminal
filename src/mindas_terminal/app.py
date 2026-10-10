"""mindas terminal: one terminal pane running the best available shell (bash first, also on Windows)."""

from __future__ import annotations

import argparse
import sys

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Static

from . import __version__, shells, theme
from .widget import TerminalPane


class TerminalApp(App[None]):
    TITLE = "space terminal"
    CSS = """
    #status { height: 1; background: $panel; color: $text-muted; padding: 0 1; }
    """
    BINDINGS = [Binding("ctrl+q", "quit", "Quit", priority=True)]

    def __init__(self, shell: shells.Shell) -> None:
        super().__init__()
        self.shell = shell

    def compose(self) -> ComposeResult:
        yield TerminalPane(self.shell, id="pane")
        yield Static(f" {self.shell.name}  |  ctrl+q quit  |  space terminal v{__version__}", id="status")

    def on_mount(self) -> None:
        theme.apply(self)
        self.query_one(TerminalPane).focus()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="mindas-terminal", description="Universal space-themed terminal")
    p.add_argument("--shell", help="shell name to use (default: the first detected, bash preferred)")
    p.add_argument("--list-shells", action="store_true", help="list detected shells and exit")
    args = p.parse_args(argv)
    found = shells.detect()
    if args.list_shells:
        for s in found:
            print(f"{s.name:<20} {' '.join(s.argv)}")
        return 0
    if not found:
        print("no shell found", file=sys.stderr)
        return 1
    shell = next((s for s in found if args.shell and args.shell.lower() in s.name.lower()), found[0])
    TerminalApp(shell).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
