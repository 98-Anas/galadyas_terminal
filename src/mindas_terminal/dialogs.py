"""Small modal dialogs: confirm, prompt for text, keyboard help."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static

DIALOG_CSS = """
.dialog { width: 72; max-width: 95%; height: auto; max-height: 90%; padding: 1 2;
          background: $surface; border: round $accent; }
.dialog .title { text-style: bold; color: $accent; margin-bottom: 1; }
.dialog .body { color: $text-muted; margin-bottom: 1; max-height: 14; }
.dialog .buttons { height: auto; align-horizontal: right; }
.dialog Button { margin-left: 1; min-width: 10; }
"""


class Confirm(ModalScreen[bool]):
    DEFAULT_CSS = "Confirm { align: center middle; }" + DIALOG_CSS
    BINDINGS = [Binding("y", "answer(True)", "Yes"), Binding("n,escape", "answer(False)", "No")]

    def __init__(self, title: str, body: str = "", ok: str = "Yes", danger: bool = True) -> None:
        super().__init__()
        self._title, self._body, self._ok, self._danger = title, body, ok, danger

    def compose(self) -> ComposeResult:
        with Vertical(classes="dialog"):
            yield Static(self._title, classes="title", markup=False)
            if self._body:
                with VerticalScroll(classes="body"):
                    yield Static(self._body, markup=False)
            with Horizontal(classes="buttons"):
                yield Button("Cancel (n)", id="no")
                yield Button(f"{self._ok} (y)", id="yes", variant="error" if self._danger else "primary")

    def on_mount(self) -> None:
        self.query_one("#no", Button).focus()          # the safe choice has focus

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "yes")

    def action_answer(self, value: bool) -> None:
        self.dismiss(value)


class Prompt(ModalScreen[str | None]):
    DEFAULT_CSS = "Prompt { align: center middle; }" + DIALOG_CSS
    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(self, title: str, value: str = "", placeholder: str = "") -> None:
        super().__init__()
        self._title, self._value, self._placeholder = title, value, placeholder

    def compose(self) -> ComposeResult:
        with Vertical(classes="dialog"):
            yield Static(self._title, classes="title", markup=False)
            yield Input(self._value, placeholder=self._placeholder)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)

    def action_cancel(self) -> None:
        self.dismiss(None)


class Help(ModalScreen[None]):
    DEFAULT_CSS = "Help { align: center middle; }" + DIALOG_CSS + "Help .dialog { width: 112; }"
    BINDINGS = [Binding("escape,q,question_mark,f1", "dismiss", "Close")]

    def __init__(self, text: str) -> None:
        super().__init__()
        self._text = text

    def compose(self) -> ComposeResult:
        with Vertical(classes="dialog"):
            yield Static("Keyboard reference  (Esc to close)", classes="title")
            with VerticalScroll():
                yield Static(self._text, markup=False)
