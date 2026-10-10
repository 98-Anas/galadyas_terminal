"""A Textual widget that runs a real shell in a pseudo-terminal and renders it with pyte.

The PTY is read on a background thread; the screen model is shared under a lock and repainted at most
30 times a second. Copy mode freezes a snapshot of scrollback plus screen and navigates it like vim.
"""

from __future__ import annotations

import os
import threading
import time
from functools import lru_cache

import pyte
from rich.color import Color
from rich.segment import Segment
from rich.style import Style
from textual import events
from textual.message import Message
from textual.strip import Strip
from textual.widget import Widget

from . import keys, paste
from .copymode import CopyMode
from .pty import Pty, spawn
from .screen import BRACKETED_PASTE, DECCKM, TerminalScreen
from .shells import Shell

_NAMED = {"brown": "yellow", "brightbrown": "bright_yellow"}
SELECT = Style(reverse=True)
MATCH = Style(bgcolor="#fbbf24", color="#070b1a")
BADGE = Style(bgcolor="#7aa2ff", color="#070b1a", bold=True)


@lru_cache(maxsize=4096)
def _color(name: str) -> Color | None:
    if name == "default":
        return None
    name = _NAMED.get(name, name)
    if len(name) == 6 and all(c in "0123456789abcdefABCDEF" for c in name):
        return Color.parse("#" + name)
    if name.startswith("bright") and not name.startswith("bright_"):
        name = "bright_" + name[6:]
    try:
        return Color.parse(name)
    except Exception:  # noqa: BLE001 - unknown colour names fall back to default
        return None


@lru_cache(maxsize=8192)
def _style(fg: str, bg: str, bold: bool, italics: bool, underscore: bool, reverse: bool) -> Style:
    f, b = _color(fg), _color(bg)
    if reverse:
        f, b = b or Color.parse("black"), f or Color.parse("white")
    return Style(color=f, bgcolor=b, bold=bold, italic=italics, underline=underscore)


def shell_env() -> dict[str, str]:
    env = dict(os.environ)
    env.update(TERM="xterm-256color", COLORTERM="truecolor", TERM_PROGRAM="mindas-terminal")
    return env


class TerminalPane(Widget, can_focus=True):
    DEFAULT_CSS = """
    TerminalPane { width: 1fr; height: 1fr; background: $background; border: round $panel; border-title-color: $text-muted; }
    TerminalPane:focus { border: round $accent; border-title-color: $accent; }
    """

    class Exited(Message):
        def __init__(self, pane: TerminalPane) -> None:
            super().__init__()
            self.pane = pane

    class Changed(Message):
        """Title or copy-mode state changed (the app refreshes tab labels and the status bar)."""

        def __init__(self, pane: TerminalPane) -> None:
            super().__init__()
            self.pane = pane

    def __init__(self, shell: Shell, scrollback: int = 10_000, cwd: str | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.shell = shell
        self.cwd = cwd
        self._screen = TerminalScreen(80, 24, scrollback)
        self._stream = pyte.Stream(self._screen)
        self._lock = threading.Lock()
        self._dirty = True
        self._pty: Pty | None = None
        self._title = ""
        self.parse_errors = 0
        self.bytes_in = 0
        self.last_output = time.monotonic()
        self.exited = False
        self._exit_reported = False
        # copy mode
        self.copy: CopyMode | None = None
        self._rows: list[dict] = []
        self.search_prompt: str | None = None      # text typed after / or ?
        self._search_forward = True

    # info
    @property
    def pid(self) -> int | None:
        return self._pty.pid if self._pty else None

    @property
    def title(self) -> str:
        return self._title or self.shell.name

    @property
    def screen_model(self) -> TerminalScreen:
        return self._screen

    # lifecycle
    def on_mount(self) -> None:
        cols, rows = max(self.size.width, 20), max(self.size.height, 5)
        self._screen.resize(rows, cols)
        self._pty = spawn(self.shell.argv, rows, cols, cwd=self.cwd, env=shell_env())
        self._screen.reply_sink = self.write          # fixed-format answers only (see TerminalScreen)
        self.border_title = self.title
        threading.Thread(target=self._reader, daemon=True, name=f"pty-{self.id}").start()
        self.set_interval(1 / 30, self._tick)

    def on_unmount(self) -> None:
        self.shutdown()

    def shutdown(self) -> None:
        pty, self._pty = self._pty, None
        if pty:
            pty.close()

    def _reader(self) -> None:
        pty = self._pty
        assert pty
        while True:
            try:
                data = pty.read()
            except Exception:  # noqa: BLE001 - EOF, closed handle, or teardown: the session is over
                break
            if not data:
                if self._pty is None or not pty.alive():
                    break
                time.sleep(0.002)
                continue
            with self._lock:
                try:
                    self._stream.feed(data)
                except Exception:  # noqa: BLE001 - one bad escape sequence must never freeze the terminal
                    self.parse_errors += 1
                    self._stream = pyte.Stream(self._screen)   # reset the parser, keep the screen
                self._dirty = True
                self.bytes_in += len(data)
                self.last_output = time.monotonic()
        self.exited = True
        self._dirty = True

    def _tick(self) -> None:
        if self._dirty:
            self._dirty = False
            if self.copy is None:
                self.refresh()
            title = self._screen.title
            if title != self._title:
                self._title = title
                self.border_title = self.title
                self.post_message(self.Changed(self))
        if self.exited and not self._exit_reported:
            self._exit_reported = True
            self.post_message(self.Exited(self))

    # output to the program
    def write(self, data: str) -> None:
        if self._pty and not self.exited:
            self._pty.write(data)

    def paste_text(self, text: str, confirmed: bool = False) -> None:
        """Paste with sanitising; a multi-line paste that would run at once asks first."""
        bracketed = BRACKETED_PASTE in self._screen.mode
        settings = getattr(self.app, "settings", None)
        ask = getattr(settings, "confirm_multiline_paste", True)
        if ask and not confirmed and paste.needs_confirmation(text, bracketed):
            from .dialogs import Confirm

            lines = paste.sanitize(text).count("\n") + 1
            self.app.push_screen(
                Confirm(f"Paste {lines} lines? Each line runs as a command.", paste.summary(text), "Paste"),
                lambda ok: ok and self.paste_text(text, confirmed=True))
            return
        self.write(paste.prepare(text, bracketed))

    # input
    def on_key(self, event: events.Key) -> None:
        event.stop()
        event.prevent_default()
        handler = getattr(self.app, "pane_key", None)
        if handler and handler(self, event):              # prefix key and its commands
            return
        if self.copy is not None:
            self._copy_key(event)
            return
        if event.key == "shift+pageup":
            self.enter_copy()
            if self.copy:
                self.copy.page(-1)
            return
        data = keys.encode(event.key, event.character, DECCKM in self._screen.mode)
        if data is not None:
            self.write(data)

    def on_paste(self, event: events.Paste) -> None:
        event.stop()
        self.paste_text(event.text)

    def on_mouse_scroll_up(self, event: events.MouseScrollUp) -> None:
        event.stop()
        if self._screen.in_alt_screen and self.copy is None:   # full-screen programs get arrow keys
            self.write(("\x1bOA" if DECCKM in self._screen.mode else "\x1b[A") * 3)
            return
        if self.copy is None:
            self.enter_copy()
        if self.copy:
            self.copy.scroll(-3)
            self.refresh()

    def on_mouse_scroll_down(self, event: events.MouseScrollDown) -> None:
        event.stop()
        if self.copy is None:
            if self._screen.in_alt_screen:
                self.write(("\x1bOB" if DECCKM in self._screen.mode else "\x1b[B") * 3)
            return
        self.copy.scroll(3)
        at_end = self.copy.top >= len(self.copy.lines) - self.copy.height
        if at_end and self.copy.anchor is None and not self.copy.query:
            self.exit_copy()                                   # scrolled back to live output
        else:
            self.refresh()

    def on_resize(self, event: events.Resize) -> None:
        cols, rows = max(self.size.width, 20), max(self.size.height, 5)
        with self._lock:
            self._screen.resize(rows, cols)
            self._dirty = True
        if self.copy:
            self.copy.height = rows
            self.copy.move()
        if self._pty:
            self._pty.resize(rows, cols)

    # copy mode
    def enter_copy(self) -> None:
        if self.copy is not None:
            return
        with self._lock:
            self._rows = self._screen.snapshot()
            lines = [self._screen.row_text(r) for r in self._rows]
            cursor = (len(self._screen.history) + self._screen.cursor.y, self._screen.cursor.x)
        self.copy = CopyMode.at_bottom(lines, self.size.height, cursor)
        self.post_message(self.Changed(self))
        self.refresh()

    def exit_copy(self) -> None:
        self.copy, self._rows, self.search_prompt = None, [], None
        self.post_message(self.Changed(self))
        self.refresh()

    def _yank(self) -> None:
        assert self.copy
        text = self.copy.selected_text()
        self.app.copy_to_clipboard(text)
        if hasattr(self.app, "paste_buffer"):
            self.app.paste_buffer = text
        self.app.notify(f"Copied {len(text)} characters", timeout=2)
        self.exit_copy()

    def _copy_key(self, event: events.Key) -> None:
        cm = self.copy
        assert cm
        key, ch = event.key, event.character
        if self.search_prompt is not None:                  # typing a search
            if key == "enter":
                if not cm.search(self.search_prompt, self._search_forward):
                    self.app.notify(f"Not found: {self.search_prompt}", severity="warning", timeout=2)
                self.search_prompt = None
            elif key == "escape":
                self.search_prompt = None
            elif key == "backspace":
                self.search_prompt = self.search_prompt[:-1]
            elif ch and ch.isprintable():
                self.search_prompt += ch
            self.refresh()
            return
        half = max(cm.height // 2, 1)
        actions = {
            "h": lambda: cm.move(cols=-1), "left": lambda: cm.move(cols=-1),
            "l": lambda: cm.move(cols=1), "right": lambda: cm.move(cols=1),
            "k": lambda: cm.move(rows=-1), "up": lambda: cm.move(rows=-1),
            "j": lambda: cm.move(rows=1), "down": lambda: cm.move(rows=1),
            "ctrl+u": lambda: cm.move(rows=-half), "ctrl+d": lambda: cm.move(rows=half),
            "ctrl+b": lambda: cm.page(-1), "pageup": lambda: cm.page(-1), "shift+pageup": lambda: cm.page(-1),
            "ctrl+f": lambda: cm.page(1), "pagedown": lambda: cm.page(1), "shift+pagedown": lambda: cm.page(1),
            "ctrl+y": lambda: cm.scroll(-1), "ctrl+e": lambda: cm.scroll(1),
            "g": cm.goto_top, "home": cm.goto_top, "G": cm.goto_bottom, "end": cm.goto_bottom,
            "0": cm.line_start, "$": cm.line_end, "^": cm.first_nonblank,
            "w": cm.word_forward, "b": cm.word_back,
            "H": lambda: cm.move(rows=cm.top - cm.row),
            "L": lambda: cm.move(rows=cm.top + cm.height - 1 - cm.row),
            "M": lambda: cm.move(rows=cm.top + cm.height // 2 - cm.row),
            "v": lambda: cm.toggle_select(False), "space": lambda: cm.toggle_select(False),
            "V": lambda: cm.toggle_select(True),
            "n": lambda: cm.next_match(self._search_forward), "N": lambda: cm.next_match(not self._search_forward),
        }
        name = ch if ch and ch in "GHLMVN$^" else key
        if name in ("y", "enter"):
            self._yank()
            return
        if name in ("q", "escape"):
            if cm.anchor is not None and name == "escape":
                cm.anchor = None
            else:
                self.exit_copy()
                return
        elif ch in ("/", "?"):
            self.search_prompt = ""
            self._search_forward = ch == "/"
        elif name in actions:
            actions[name]()
        self.post_message(self.Changed(self))
        self.refresh()

    # rendering
    def _base_style(self) -> Style:
        """Theme colours under the program's own: "default" cells take the pane background and text colour."""
        styles = self.styles
        key = (styles.background.hex, styles.color.hex)
        if key != getattr(self, "_base_key", None):
            self._base_key = key
            self._base = Style(bgcolor=styles.background.rich_color, color=styles.color.rich_color)
            self._combined: dict[tuple, Style] = {}       # cell attributes -> merged style, per theme
        return self._base

    def render_line(self, y: int) -> Strip:
        width = self.size.width
        if self.copy is not None:
            return self._render_copy_line(y, width)
        with self._lock:
            screen = self._screen
            if y >= screen.lines:
                return Strip.blank(width)
            cursor_x = screen.cursor.x if (y == screen.cursor.y and not screen.cursor.hidden
                                           and self.has_focus) else -1
            return self._strip(screen.buffer[y], screen.columns, lambda x: SELECT if x == cursor_x else None)

    def _render_copy_line(self, y: int, width: int) -> Strip:
        cm = self.copy
        assert cm
        if self.search_prompt is not None and y == cm.height - 1:
            text = ("/" if self._search_forward else "?") + self.search_prompt
            return Strip([Segment(text.ljust(width)[:width], BADGE)], width)
        r = cm.top + y
        if r >= len(self._rows):
            return Strip.blank(width)

        def overlay(x: int) -> Style | None:
            if (r == cm.row and x == cm.col) or cm.selected(r, x):
                return SELECT
            if cm.query and cm.match_at(r, x):
                return MATCH
            return None

        strip = self._strip(self._rows[r], self._screen.columns, overlay)
        if y == 0:                                           # position badge, top right, like tmux
            badge = f" [{cm.row + 1}/{len(cm.lines)}] "
            strip = Strip.join([strip.crop(0, max(width - len(badge), 0)), Strip([Segment(badge, BADGE)])])
        return strip

    def _strip(self, row: dict, columns: int, overlay) -> Strip:
        default = self._screen.default_char
        base = self._base_style()
        cache = self._combined
        segments: list[Segment] = []
        run_text: list[str] = []
        run_style: Style | None = None
        for x in range(columns):
            ch = row.get(x, default)
            attrs = (ch.fg, ch.bg, ch.bold, ch.italics, ch.underscore, ch.reverse)
            style = cache.get(attrs)
            if style is None:
                style = cache[attrs] = base + _style(*attrs)
            extra = overlay(x)
            if extra is not None:
                style = style + extra
            if style != run_style and run_text:
                segments.append(Segment("".join(run_text), run_style))
                run_text = []
            run_style = style
            run_text.append(ch.data)          # "" after a wide character: it already covers two cells
        if run_text:
            segments.append(Segment("".join(run_text), run_style))
        return Strip(segments, columns)
