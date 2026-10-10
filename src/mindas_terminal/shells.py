"""Find the shells available on this machine. Bash first, also on Windows."""

from __future__ import annotations

import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Shell:
    name: str
    argv: tuple[str, ...]


WINDOWS_BASH_CANDIDATES = (
    ("Git Bash", r"C:\Program Files\Git\bin\bash.exe"),
    ("Git Bash", r"C:\Program Files (x86)\Git\bin\bash.exe"),
    ("MSYS2 bash", r"C:\msys64\usr\bin\bash.exe"),
)


def detect(platform: str = sys.platform, exists=os.path.exists, which=shutil.which) -> list[Shell]:
    """Available shells, best first: bash is preferred so navigation works the same on Windows and Linux."""
    found: list[Shell] = []
    if platform == "win32":
        for name, path in WINDOWS_BASH_CANDIDATES:
            if exists(path):
                found.append(Shell(name, (path, "--login", "-i")))
                break
        if which("wsl.exe"):
            found.append(Shell("WSL bash", ("wsl.exe", "--cd", "~")))
        for name, exe in (("PowerShell 7", "pwsh.exe"), ("Windows PowerShell", "powershell.exe"), ("cmd", "cmd.exe")):
            if path := which(exe):
                found.append(Shell(name, (path, "-NoLogo") if "powershell" in exe.lower() or "pwsh" in exe else (path,)))
    else:
        for name in ("bash", "zsh", "fish", "sh"):
            if path := which(name):
                found.append(Shell(name, (path, "-i") if name != "fish" else (path,)))
        user = os.environ.get("SHELL")
        if user and Path(user).name not in {s.name for s in found} and exists(user):
            found.insert(0, Shell(Path(user).name, (user, "-i")))
    return found
