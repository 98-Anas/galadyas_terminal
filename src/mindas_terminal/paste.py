"""Safe paste. Pure.

Pasted text is a classic attack path: a web page can hide a newline (runs the command immediately) or an
escape sequence (ends bracketed paste early, then runs the rest) inside text that looks harmless.

- Control characters are removed, except tab and newline; this also removes any embedded `ESC[201~`.
- Newlines become carriage returns, which is what a terminal sends for Enter.
- When the program asked for bracketed paste (mode 2004), the text is wrapped so the shell inserts it
  without running it. Otherwise a paste that contains a newline needs confirmation first.
"""

from __future__ import annotations

START, END = "\x1b[200~", "\x1b[201~"


def sanitize(text: str) -> str:
    """Also drops invisible format characters such as bidi overrides (the "trojan source" trick)."""
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\xa0", " ")
    return "".join(c for c in text if c in "\t\n" or c.isprintable())


def prepare(text: str, bracketed: bool) -> str:
    body = sanitize(text).replace("\n", "\r")
    return f"{START}{body}{END}" if bracketed else body


def needs_confirmation(text: str, bracketed: bool) -> bool:
    """True when pasting would run commands immediately."""
    return not bracketed and "\n" in sanitize(text)


def summary(text: str, limit: int = 8) -> str:
    lines = sanitize(text).split("\n")
    shown = "\n".join(line[:100] for line in lines[:limit])
    more = f"\n... and {len(lines) - limit} more lines" if len(lines) > limit else ""
    return shown + more
