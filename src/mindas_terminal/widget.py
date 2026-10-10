"""A Textual widget that runs a real shell in a pseudo-terminal and renders it with pyte."""

from __future__ import annotations

import threading
import time
from functools import lru_cache

import pyte
from rich.color import Color
from rich.segment import Segment
from rich.style import Style
from textual import events
from textual.geometry import Size
from textual.strip import Strip
from textual.widget import Widget

from . import keys
from .pty import Pty, spawn
from .shells import Shell

_NAMED = {"brown": "yellow", "brightbrown": "bright_yellow"}
DECCKM = 1 << 5   # application cursor keys (private mode 1); pyte stores private modes shifted by 5


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


class TolerantScreen(pyte.Screen):
    """A pyte screen that ignores sequences pyte does not implement instead of failing.

    Example: vim sends `CSI > 4;1 m` (xterm modifyOtherKeys), a private SGR that pyte rejects.
    """

    ALT_SCREEN = (1049, 1047, 47)    # private modes for the alternate screen (vim, less, htop)

    def __init__(self, columns: int, lines: int) -> None:
        super().__init__(columns, lines)
        self._saved: tuple | None = None

    def select_graphic_rendition(self, *attrs, private: bool = False, **_ignored) -> None:
        if private:
            return
        super().select_graphic_rendition(*attrs)

    def set_mode(self, *modes, **kwargs) -> None:
        if kwargs.get("private") and any(m in self.ALT_SCREEN for m in modes) and self._saved is None:
            # Enter the alternate screen: remember the normal screen, then start clean.
            self._saved = ({y: dict(line) for y, line in self.buffer.items()}, self.cursor.x, self.cursor.y)
            self.erase_in_display(2)
            self.cursor_position()
        super().set_mode(*modes, **kwargs)

    def reset_mode(self, *modes, **kwargs) -> None:
        if kwargs.get("private") and any(m in self.ALT_SCREEN for m in modes) and self._saved is not None:
            # Leave the alternate screen: restore what was there before the full-screen program started.
            lines, x, y = self._saved
            self._saved = None
            self.buffer.clear()
            for row, line in lines.items():
                if row < self.lines:
                    self.buffer[row].update({col: ch for col, ch in line.items() if col < self.columns})
            self.cursor.x, self.cursor.y = min(x, self.columns - 1), min(y, self.lines - 1)
            self.dirty.update(range(self.lines))
        super().reset_mode(*modes, **kwargs)


class TerminalPane(Widget, can_focus=True):
    DEFAULT_CSS = "TerminalPane { width: 1fr; height: 1fr; }"

    def __init__(self, shell: Shell, **kwargs) -> None:
        super().__init__(**kwargs)
        self.shell = shell
        self._screen = TolerantScreen(80, 24)
        self._stream = pyte.Stream(self._screen)
        self.parse_errors = 0
        self._lock = threading.Lock()
        self._dirty = True
        self._pty: Pty | None = None
        self.bytes_in = 0
        self.last_output = time.monotonic()
        self.exited = False

    # lifecycle
    def on_mount(self) -> None:
        cols, rows = max(self.size.width, 20), max(self.size.height, 5)
        self._screen.resize(rows, cols)
        self._pty = spawn(self.shell.argv, rows, cols)
        threading.Thread(target=self._reader, daemon=True).start()
        self.set_interval(1 / 30, self._tick)

    def on_unmount(self) -> None:
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
            self.refresh()

    # input
    def write(self, data: str) -> None:
        if self._pty and not self.exited:
            self._pty.write(data)

    def on_key(self, event: events.Key) -> None:
        app_cursor = DECCKM in self._screen.mode
        data = keys.encode(event.key, event.character, app_cursor)
        if data is not None:
            event.stop()
            event.prevent_default()
            self.write(data)

    def on_paste(self, event: events.Paste) -> None:
        self.write(event.text)

    def on_resize(self, event: events.Resize) -> None:
        cols, rows = max(event.size.width, 20), max(event.size.height, 5)
        with self._lock:
            self._screen.resize(rows, cols)
            self._dirty = True
        if self._pty:
            self._pty.resize(rows, cols)

    # rendering
    def get_content_width(self, container: Size, viewport: Size) -> int:
        return container.width

    def render_line(self, y: int) -> Strip:
        with self._lock:
            screen = self._screen
            if y >= screen.lines:
                return Strip.blank(self.size.width)
            row = screen.buffer[y]
            cursor = (screen.cursor.x, screen.cursor.y) if not screen.cursor.hidden and self.has_focus else None
            segments: list[Segment] = []
            run_text: list[str] = []
            run_style: Style | None = None
            for x in range(screen.columns):
                ch = row[x]
                style = _style(ch.fg, ch.bg, ch.bold, ch.italics, ch.underscore, ch.reverse)
                if cursor == (x, y):
                    style = style + Style(reverse=True)
                if style is not run_style and run_text:
                    segments.append(Segment("".join(run_text), run_style))
                    run_text = []
                run_style = style
                run_text.append(ch.data or " ")
            if run_text:
                segments.append(Segment("".join(run_text), run_style))
        return Strip(segments, screen.columns)
