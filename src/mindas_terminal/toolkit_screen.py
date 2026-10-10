"""Toolkit browser: search curated commands, fill placeholders, insert at the prompt (never run)."""

from __future__ import annotations

import sys

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, OptionList, Static
from textual.widgets.option_list import Option

from . import toolkit


class ToolkitScreen(ModalScreen[str | None]):
    """Returns the command to insert, or None."""

    DEFAULT_CSS = """
    ToolkitScreen { align: center middle; }
    #tk { width: 110; max-width: 96%; height: 85%; background: $surface; border: round $accent; padding: 0 1; }
    #tk-title { color: $accent; text-style: bold; height: 1; margin-top: 1; }
    #tk Input { width: 100%; margin: 0 0 1 0; }
    #tk-list { height: 1fr; border: none; background: $surface; }
    #tk-detail { height: auto; max-height: 6; color: $text-muted; border-top: solid $panel; padding-top: 0; }
    """
    BINDINGS = [Binding("escape", "close", "Close"), Binding("down", "down", show=False), Binding("up", "up", show=False)]

    def __init__(self, profile: str | None = None, platform: str = sys.platform) -> None:
        super().__init__()
        self.profile = profile
        self.tools = toolkit.for_platform(platform)
        self.shown: list[toolkit.Tool] = []

    def compose(self) -> ComposeResult:
        with Vertical(id="tk"):
            yield Static(f"Toolkits  {len(self.tools)} commands for {len(toolkit.FIELDS)} fields   "
                         "Enter insert (never runs)  Esc close", id="tk-title")
            yield Input(placeholder="search: e.g. docker logs, slurm gpu, tls cert, parquet, failed logins")
            yield OptionList(id="tk-list")
            yield Static("", id="tk-detail")

    def on_mount(self) -> None:
        self.call_after_refresh(self._fill, "")
        self.query_one(Input).focus()

    def _fill(self, query: str) -> None:
        self.shown = toolkit.search(self.tools, query, self.profile)
        ol = self.query_one(OptionList)
        ol.clear_options()
        for t in self.shown:
            line = Text()
            line.append(f"{toolkit.FIELDS[t.field][:24]:<25}", style="#b18cff")
            line.append(f"{t.title[:46]:<47}", style="bold")
            width = max(self.size.width - 80, 20)
            cmd = t.command if len(t.command) <= width else t.command[:width - 1] + "…"
            line.append(cmd, style="#5eead4")
            ol.add_option(Option(line))
        if self.shown:
            ol.highlighted = 0
        self._detail()

    def _detail(self) -> None:
        ol = self.query_one(OptionList)
        idx = ol.highlighted
        detail = self.query_one("#tk-detail", Static)
        if idx is None or idx >= len(self.shown):
            detail.update("No match. Try fewer words." if not self.shown else "")
            return
        t = self.shown[idx]
        text = Text()
        text.append(t.command + "\n", style="#5eead4")
        if t.note:
            text.append(t.note + "\n")
        if ph := toolkit.placeholders(t.command):
            text.append("You will be asked for: " + ", ".join(ph), style="#fbbf24")
        detail.update(text)

    def on_input_changed(self, event: Input.Changed) -> None:
        self._fill(event.value)

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        self._detail()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._choose(self.query_one(OptionList).highlighted)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self._choose(event.option_index)

    def action_down(self) -> None:
        self.query_one(OptionList).action_cursor_down()

    def action_up(self) -> None:
        self.query_one(OptionList).action_cursor_up()

    def action_close(self) -> None:
        self.dismiss(None)

    def _choose(self, idx: int | None) -> None:
        if idx is None or idx >= len(self.shown):
            return
        self._ask(self.shown[idx].command, toolkit.placeholders(self.shown[idx].command))

    def _ask(self, command: str, names: list[str]) -> None:
        """Ask for each placeholder in turn; an empty answer keeps the placeholder for editing at the prompt."""
        from .dialogs import Prompt

        if not names:
            self.dismiss(command)
            return
        name, rest = names[0], names[1:]

        def got(value: str | None) -> None:
            if value is None:
                return
            value = value.strip()
            self._ask(command.replace(f"<{name}>", toolkit.quote(value)) if value else command, rest)

        self.app.push_screen(Prompt(f"Value for <{name}>", placeholder=f"{name} (leave empty to edit later)"), got)
