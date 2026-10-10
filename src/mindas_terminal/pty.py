"""Pseudo-terminal adapter: ConPTY (pywinpty) on Windows, a POSIX pty (ptyprocess) on Linux.

Both expose the same small interface: read text, write text, resize, alive, close.
"""

from __future__ import annotations

import sys
from typing import Protocol


class Pty(Protocol):
    def read(self) -> str: ...
    def write(self, data: str) -> None: ...
    def resize(self, rows: int, cols: int) -> None: ...
    def alive(self) -> bool: ...
    def close(self) -> None: ...


class WindowsPty:
    """ConPTY through pywinpty's low-level PTY API.

    Measured on Git Bash, `seq 1 100000`: the high-level PtyProcess wrapper took 97.7 s (output arrives in
    tiny chunks); this API takes 8.9 s. read() is non-blocking and returns '' when nothing is available.
    """

    def __init__(self, argv: tuple[str, ...], rows: int, cols: int, cwd: str | None = None, env: dict | None = None):
        import subprocess

        import winpty  # pywinpty

        self._p = winpty.PTY(cols, rows, backend=winpty.Backend.ConPTY)
        cmdline = " " + subprocess.list2cmdline(list(argv[1:])) if len(argv) > 1 else None
        env_block = "\0".join(f"{k}={v}" for k, v in env.items()) + "\0" if env else None
        self._p.spawn(argv[0], cmdline=cmdline, cwd=cwd, env=env_block)

    def read(self) -> str:
        return self._p.read(blocking=False)

    def write(self, data: str) -> None:
        self._p.write(data)

    def resize(self, rows: int, cols: int) -> None:
        self._p.set_size(cols, rows)

    def alive(self) -> bool:
        return self._p.isalive()

    def close(self) -> None:
        try:
            self._p.cancel_io()
        except Exception:  # noqa: BLE001 - closing must never raise
            pass
        self._p = None  # releasing the PTY ends the child process


class PosixPty:
    def __init__(self, argv: tuple[str, ...], rows: int, cols: int, cwd: str | None = None, env: dict | None = None):
        from ptyprocess import PtyProcessUnicode

        self._p = PtyProcessUnicode.spawn(list(argv), dimensions=(rows, cols), cwd=cwd, env=env)

    def read(self) -> str:
        return self._p.read(65536)

    def write(self, data: str) -> None:
        self._p.write(data)

    def resize(self, rows: int, cols: int) -> None:
        self._p.setwinsize(rows, cols)

    def alive(self) -> bool:
        return self._p.isalive()

    def close(self) -> None:
        try:
            self._p.terminate(force=True)
        except Exception:  # noqa: BLE001
            pass


def spawn(argv: tuple[str, ...], rows: int, cols: int, cwd: str | None = None, env: dict | None = None) -> Pty:
    cls = WindowsPty if sys.platform == "win32" else PosixPty
    return cls(argv, rows, cols, cwd, env)
