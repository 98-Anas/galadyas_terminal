"""The terminal screen model: pyte plus the pieces a daily-use terminal needs.

- Tolerates sequences pyte does not implement instead of failing (a bad sequence must never freeze a pane).
- Alternate screen (private modes 1049, 1047, 47): full-screen programs hand the shell screen back on exit.
- Scrollback: lines that scroll off the top are kept in a bounded in-memory buffer (never written to disk).
- Window titles set by programs are sanitised: printable characters only, bounded length.
"""

from __future__ import annotations

import re
from collections import deque

import pyte

ALT_SCREEN = (1049, 1047, 47)
DECCKM = 1 << 5            # application cursor keys; pyte stores private modes shifted by 5
BRACKETED_PASTE = 2004 << 5
TITLE_MAX = 60
SAFE_REPLY = re.compile(r"\x1b\[(?:\d{1,5};\d{1,5}R|\?[\d;]{1,20}c|0n)")


def clean_title(title: str) -> str:
    """Printable characters only, so a program cannot inject control sequences through its title."""
    return "".join(c for c in title if c.isprintable())[:TITLE_MAX].strip()


class TerminalScreen(pyte.Screen):
    def __init__(self, columns: int, lines: int, scrollback: int = 10_000) -> None:
        super().__init__(columns, lines)
        self._saved: tuple | None = None
        self.reply_sink = None             # callable that writes to the program; set by the pane
        self.history: deque[dict] = deque(maxlen=max(scrollback, 0) or None)
        self.scrollback = scrollback

    @property
    def in_alt_screen(self) -> bool:
        return self._saved is not None

    # scrollback
    def index(self) -> None:
        top, bottom = self.margins or pyte.screens.Margins(0, self.lines - 1)
        if self.cursor.y == bottom and top == 0 and self._saved is None and self.scrollback:
            self.history.append(dict(self.buffer[0]))
        super().index()

    def erase_in_display(self, how: int = 0, *args, **kwargs) -> None:
        if how == 3:                       # `clear` asks for the scrollback to be erased too
            self.history.clear()
            return
        super().erase_in_display(how, *args, **kwargs)

    # answers to programs
    def write_process_input(self, data: str) -> None:
        """Only fixed-format answers (cursor position, device attributes, status OK) go back to the program.

        Terminals that echo attacker-controlled data back (titles, unknown queries) let a file you `cat` type
        commands into your shell; nothing of that kind is ever answered here.
        """
        if self.reply_sink is not None and SAFE_REPLY.fullmatch(data):
            self.reply_sink(data)

    # tolerance
    def select_graphic_rendition(self, *attrs, private: bool = False, **_ignored) -> None:
        if private:                        # e.g. vim's `CSI > 4;1 m` (xterm modifyOtherKeys)
            return
        super().select_graphic_rendition(*attrs)

    def set_title(self, param: str) -> None:
        super().set_title(clean_title(param))

    def set_icon_name(self, param: str) -> None:
        super().set_icon_name(clean_title(param))

    # alternate screen
    def set_mode(self, *modes, **kwargs) -> None:
        if kwargs.get("private") and any(m in ALT_SCREEN for m in modes) and self._saved is None:
            self._saved = ({y: dict(line) for y, line in self.buffer.items()}, self.cursor.x, self.cursor.y)
            self.erase_in_display(2)
            self.cursor_position()
        super().set_mode(*modes, **kwargs)

    def reset_mode(self, *modes, **kwargs) -> None:
        if kwargs.get("private") and any(m in ALT_SCREEN for m in modes) and self._saved is not None:
            lines, x, y = self._saved
            self._saved = None
            self.buffer.clear()
            for row, line in lines.items():
                if row < self.lines:
                    self.buffer[row].update({col: ch for col, ch in line.items() if col < self.columns})
            self.cursor.x, self.cursor.y = min(x, self.columns - 1), min(y, self.lines - 1)
            self.dirty.update(range(self.lines))
        super().reset_mode(*modes, **kwargs)

    # views
    def snapshot(self) -> list[dict]:
        """Scrollback plus the visible screen, oldest first. Rows are copies, safe to read without the lock."""
        rows = list(self.history)
        rows.extend(dict(self.buffer[y]) for y in range(self.lines))
        return rows

    def row_text(self, row: dict) -> str:
        return "".join((row[x].data if x in row else " ") or "" for x in range(self.columns)).rstrip()
