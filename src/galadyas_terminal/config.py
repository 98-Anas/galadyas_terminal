"""User settings: a small TOML file, read as data only (never executed). Command-line options win.

Location: %APPDATA%\\galadyas-terminal\\config.toml on Windows, $XDG_CONFIG_HOME/galadyas-terminal/config.toml
(default ~/.config) elsewhere. Unknown keys and wrong types are ignored with a warning, never fatal.
"""

from __future__ import annotations

import os
import shutil
import sys
import tomllib
from dataclasses import asdict, dataclass, fields, replace  # noqa: F401 - replace is re-exported
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    shell: str = ""                    # name from --list-shells; empty = best found (bash first)
    prefix: str = "ctrl+b"
    scrollback: int = 10_000
    profile: str = ""                  # toolkit field listed first
    theme: str = "space"
    alias_style: str = "linux"         # linux: Linux command names in PowerShell too; native: PowerShell only
    confirm_multiline_paste: bool = True
    show_home: bool = True             # start with the home window
    remember_history: bool = True      # keep commands for autocomplete (secrets are never stored)


THEMES = ("space", "light", "contrast")
PREFIXES = ("ctrl+b", "ctrl+a", "ctrl+space", "ctrl+backslash")
ALIAS_STYLES = ("linux", "native")


def path() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    folder = base / "galadyas-terminal"
    legacy = base / "mindas-terminal"          # name before 0.4.0
    if not folder.exists() and legacy.is_dir():
        try:
            shutil.copytree(legacy, folder)
        except OSError:
            return legacy / "config.toml"
    return folder / "config.toml"


def parse(text: str) -> tuple[Settings, list[str]]:
    """Settings from TOML text, plus warnings for anything ignored."""
    warnings: list[str] = []
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        return Settings(), [f"config ignored: {exc}"]
    known = {f.name: f.type for f in fields(Settings)}
    values = {}
    for key, value in data.items():
        if key not in known:
            warnings.append(f"unknown setting ignored: {key}")
            continue
        want = {"str": str, "int": int, "bool": bool}[known[key]]
        if type(value) is not want:
            warnings.append(f"setting {key} must be {known[key]}")
            continue
        values[key] = value
    s = replace(Settings(), **values)
    checks = [("theme", THEMES), ("alias_style", ALIAS_STYLES)]
    for key, allowed in checks:
        if getattr(s, key) not in allowed:
            warnings.append(f"{key} must be one of {', '.join(allowed)}")
            s = replace(s, **{key: getattr(Settings(), key)})
    if not 0 <= s.scrollback <= 1_000_000:
        warnings.append("scrollback must be between 0 and 1000000")
        s = replace(s, scrollback=Settings().scrollback)
    return s, warnings


def load() -> tuple[Settings, list[str]]:
    p = path()
    try:
        return parse(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return Settings(), []
    except OSError as exc:
        return Settings(), [f"config not readable: {exc}"]


def dumps(s: Settings) -> str:
    lines = ["# galadyas-terminal settings. Data only; see the wiki page Configuration."]
    for key, value in asdict(s).items():
        if isinstance(value, bool):
            lines.append(f"{key} = {'true' if value else 'false'}")
        elif isinstance(value, int):
            lines.append(f"{key} = {value}")
        else:
            escaped = "".join(c for c in str(value) if c.isprintable()).replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'{key} = "{escaped}"')
    return "\n".join(lines) + "\n"


def history_path() -> Path:
    return path().parent / "history.tsv"


def save_private(target: Path, text: str) -> None:
    """Write atomically, readable by the owner only (history can reveal what you work on)."""
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(".tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, target)


def save(s: Settings) -> Path:
    p = path()
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(dumps(s), encoding="utf-8")
    os.replace(tmp, p)                  # atomic: a crash never leaves a half-written file
    return p
