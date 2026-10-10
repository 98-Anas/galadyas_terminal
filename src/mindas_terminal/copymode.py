"""Copy mode: vim-style navigation, search and selection over scrollback. Pure logic, no UI.

Works on a frozen list of text lines, so output that keeps arriving does not move the cursor.
"""

from __future__ import annotations

from dataclasses import dataclass, field


def _is_word(c: str) -> bool:
    return c.isalnum() or c == "_"


@dataclass
class CopyMode:
    lines: list[str]
    height: int
    row: int = 0
    col: int = 0
    top: int = 0
    anchor: tuple[int, int] | None = None      # selection start
    linewise: bool = False
    query: str = ""
    matches: list[tuple[int, int]] = field(default_factory=list)
    _by_row: dict[int, list[int]] = field(default_factory=dict, repr=False)

    @classmethod
    def at_bottom(cls, lines: list[str], height: int, cursor: tuple[int, int] | None = None) -> CopyMode:
        cm = cls(lines=lines or [""], height=max(height, 1))
        cm.row = len(cm.lines) - 1 if cursor is None else cursor[0]
        cm.col = 0 if cursor is None else cursor[1]
        cm.top = max(len(cm.lines) - cm.height, 0)
        cm._clamp()
        return cm

    # geometry
    def _clamp(self) -> None:
        self.row = min(max(self.row, 0), len(self.lines) - 1)
        self.col = min(max(self.col, 0), max(len(self.lines[self.row]) - 1, 0))
        if self.row < self.top:
            self.top = self.row
        elif self.row >= self.top + self.height:
            self.top = self.row - self.height + 1
        self.top = min(max(self.top, 0), max(len(self.lines) - self.height, 0))

    def move(self, rows: int = 0, cols: int = 0) -> None:
        self.row += rows
        self.col += cols
        self._clamp()

    def scroll(self, rows: int) -> None:
        """Scroll the view and carry the cursor along (mouse wheel, Ctrl+E/Ctrl+Y)."""
        self.top = min(max(self.top + rows, 0), max(len(self.lines) - self.height, 0))
        self.row = min(max(self.row, self.top), self.top + self.height - 1)
        self._clamp()

    def page(self, fraction: float) -> None:
        self.move(rows=int(self.height * fraction) or (1 if fraction > 0 else -1))

    def goto_top(self) -> None:
        self.row, self.col = 0, 0
        self._clamp()

    def goto_bottom(self) -> None:
        self.row, self.col = len(self.lines) - 1, 0
        self._clamp()

    def line_start(self) -> None:
        self.col = 0

    def line_end(self) -> None:
        self.col = max(len(self.lines[self.row]) - 1, 0)

    def first_nonblank(self) -> None:
        line = self.lines[self.row]
        self.col = len(line) - len(line.lstrip())
        self._clamp()

    def word_forward(self) -> None:
        r, c = self.row, self.col
        line = self.lines[r]
        while c < len(line) and _is_word(line[c]):
            c += 1
        while True:
            while c < len(line) and not _is_word(line[c]):
                c += 1
            if c < len(line) or r == len(self.lines) - 1:
                break
            r, c = r + 1, 0
            line = self.lines[r]
        self.row, self.col = r, c
        self._clamp()

    def word_back(self) -> None:
        r, c = self.row, self.col - 1
        while True:
            line = self.lines[r]
            while c >= 0 and not _is_word(line[c]):
                c -= 1
            if c >= 0 or r == 0:
                break
            r = r - 1
            c = len(self.lines[r]) - 1
        while c > 0 and _is_word(self.lines[r][c - 1]):
            c -= 1
        self.row, self.col = r, max(c, 0)
        self._clamp()

    # selection
    def toggle_select(self, linewise: bool = False) -> None:
        if self.anchor is not None and self.linewise == linewise:
            self.anchor = None
        else:
            self.anchor = self.anchor or (self.row, self.col)
            self.linewise = linewise

    def selection(self) -> tuple[tuple[int, int], tuple[int, int]] | None:
        if self.anchor is None:
            return None
        a, b = sorted([self.anchor, (self.row, self.col)])
        if self.linewise:
            return (a[0], 0), (b[0], max(len(self.lines[b[0]]), 1) - 1)
        return a, b

    def selected(self, row: int, col: int) -> bool:
        sel = self.selection()
        if sel is None:
            return False
        (r0, c0), (r1, c1) = sel
        if row < r0 or row > r1:
            return False
        if self.linewise:
            return True
        if row == r0 and col < c0:
            return False
        if row == r1 and col > c1:
            return False
        return True

    def selected_text(self) -> str:
        sel = self.selection()
        if sel is None:
            return self.lines[self.row]
        (r0, c0), (r1, c1) = sel
        if r0 == r1:
            return self.lines[r0][c0:c1 + 1]
        parts = [self.lines[r0][c0:]] + self.lines[r0 + 1:r1] + [self.lines[r1][:c1 + 1]]
        return "\n".join(p.rstrip() for p in parts)

    # search (case-insensitive unless the query has a capital letter, like vim's smartcase)
    def search(self, query: str, forward: bool = True) -> bool:
        self.query = query
        if not query:
            self.matches, self._by_row = [], {}
            return False
        sensitive = any(c.isupper() for c in query)
        needle = query if sensitive else query.lower()
        self.matches, self._by_row = [], {}
        for r, line in enumerate(self.lines):
            text, start = (line if sensitive else line.lower()), 0
            while (i := text.find(needle, start)) != -1:
                self.matches.append((r, i))
                self._by_row.setdefault(r, []).append(i)
                start = i + 1
        return self.next_match(forward, include_current=False)

    def next_match(self, forward: bool = True, include_current: bool = False) -> bool:
        if not self.matches:
            return False
        here = (self.row, self.col)
        if forward:
            cands = [m for m in self.matches if m > here or (include_current and m == here)]
            target = cands[0] if cands else self.matches[0]
        else:
            cands = [m for m in self.matches if m < here]
            target = cands[-1] if cands else self.matches[-1]
        self.row, self.col = target
        self._clamp()
        return True

    def match_at(self, row: int, col: int) -> bool:
        n = len(self.query)
        return bool(n) and any(c <= col < c + n for c in self._by_row.get(row, ()))
