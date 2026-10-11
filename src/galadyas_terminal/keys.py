"""Translate Textual key events into the byte sequences a terminal program expects (xterm style). Pure."""

from __future__ import annotations

SPECIAL = {
    "enter": "\r", "tab": "\t", "shift+tab": "\x1b[Z", "backspace": "\x7f", "escape": "\x1b",
    "up": "\x1b[A", "down": "\x1b[B", "right": "\x1b[C", "left": "\x1b[D",
    "home": "\x1b[H", "end": "\x1b[F", "insert": "\x1b[2~", "delete": "\x1b[3~",
    "pageup": "\x1b[5~", "pagedown": "\x1b[6~",
    "f1": "\x1bOP", "f2": "\x1bOQ", "f3": "\x1bOR", "f4": "\x1bOS", "f5": "\x1b[15~", "f6": "\x1b[17~",
    "f7": "\x1b[18~", "f8": "\x1b[19~", "f9": "\x1b[20~", "f10": "\x1b[21~", "f11": "\x1b[23~", "f12": "\x1b[24~",
    "ctrl+left": "\x1b[1;5D", "ctrl+right": "\x1b[1;5C", "ctrl+up": "\x1b[1;5A", "ctrl+down": "\x1b[1;5B",
}
APP_CURSOR = {"up": "\x1bOA", "down": "\x1bOB", "right": "\x1bOC", "left": "\x1bOD"}


def encode(key: str, character: str | None, app_cursor: bool = False) -> str | None:
    """Bytes for a key, or None if the key should not be sent to the program."""
    if app_cursor and key in APP_CURSOR:
        return APP_CURSOR[key]
    if key in SPECIAL:
        return SPECIAL[key]
    if key.startswith("ctrl+") and len(key) == 6 and key[5].isalpha():
        return chr(ord(key[5].lower()) - 96)          # ctrl+a .. ctrl+z
    if key.startswith("alt+") and character:
        return "\x1b" + character
    if character and character.isprintable():
        return character
    return None
