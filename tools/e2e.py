"""End-to-end checks: real shells inside the terminal, headless, with measurements.

Usage: uv run python tools/e2e.py [OUT_DIR]
"""

import asyncio
import sys
import time
from pathlib import Path

import psutil

from galadyas_terminal import shells
from galadyas_terminal.app import TerminalApp
from galadyas_terminal.config import Settings
from galadyas_terminal.widget import TerminalPane

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")


def screen_text(pane: TerminalPane) -> str:
    with pane._lock:
        return "\n".join(pane._screen.display)


async def wait_for(pane: TerminalPane, needle: str, timeout: float = 30.0) -> float:
    start = time.monotonic()
    while time.monotonic() - start < timeout:
        if needle in screen_text(pane):
            return time.monotonic() - start
        await asyncio.sleep(0.05)
    raise TimeoutError(f"did not see {needle!r}; screen:\n{screen_text(pane)[-800:]}")


async def run(shell_name: str, steps) -> None:
    shell = next(s for s in shells.detect() if shell_name.lower() in s.name.lower())
    app = TerminalApp(shell, settings=Settings(show_home=False, remember_history=False))
    async with app.run_test(size=(110, 32)) as pilot:
        pane = app.query_one(TerminalPane)
        await asyncio.sleep(2.5)                     # shell start-up
        for step in steps:
            await step(app, pane, pilot)


FAILED: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    if not ok:
        FAILED.append(label)
    print(f"{'PASS' if ok else 'FAIL'}  {label}  {detail}")


async def bash() -> None:
    async def basics(app, pane, pilot):
        pane.write("echo READY-$((6*7)); printf '\\033[31mRED\\033[0m %s\\n' ok\r")
        t = await wait_for(pane, "READY-42")
        check("bash: command runs and output renders", True, f"{t:.2f}s")
        check("bash: ANSI colour sequences parsed", "RED ok" in screen_text(pane))

    async def unicode(app, pane, pilot):
        pane.write("echo 'symbols: ✓ → ü ──'\r")
        await wait_for(pane, "symbols")
        check("Unicode characters reach the screen", "✓ → ü" in screen_text(pane))

    async def throughput(app, pane, pilot):
        proc = psutil.Process()
        cpu0, t0 = proc.cpu_times(), time.monotonic()
        pane.write("seq 1 100000; echo DONE-$((1+1))\r")      # the marker exists only in the output
        await wait_for(pane, "DONE-2", timeout=120)
        elapsed = time.monotonic() - t0
        cpu1 = proc.cpu_times()
        cpu = (cpu1.user - cpu0.user) + (cpu1.system - cpu0.system)
        check("Throughput: 100,000 lines", elapsed < 30, f"{elapsed:.1f}s wall, {cpu:.1f}s app CPU, {100000/elapsed:,.0f} lines/s")

    async def keys(app, pane, pilot):
        pane.write("sleep 30; echo SLEPT-$((9+9))\r")
        await asyncio.sleep(1.0)
        t0 = time.monotonic()
        await pilot.press("ctrl+c")
        pane.write("echo AFTER-$((2+3))\r")
        t = await wait_for(pane, "AFTER-5", timeout=20)
        interrupted = "SLEPT-18" not in screen_text(pane)
        check("Ctrl+C interrupts a running command", interrupted and t < 10, f"{time.monotonic() - t0:.2f}s")
        await pilot.press(*"echo TYPED-$((4+4))", "enter")
        await wait_for(pane, "TYPED-8")
        check("Typed keys reach the shell", True)

    async def fullscreen(app, pane, pilot):
        pane.write("vim -u NONE -N\r")
        await wait_for(pane, "~", timeout=15)
        await asyncio.sleep(1.0)
        app.save_screenshot(filename="e2e-vim.svg", path=str(OUT))
        check("Full-screen program (vim) renders", screen_text(pane).count("~") > 5)
        pane.write("\x1b")                          # Escape alone, then the command (else it reads as Alt+:)
        await asyncio.sleep(0.3)
        pane.write(":q!\r")
        await asyncio.sleep(1.0)                      # vim discards typeahead when it exits
        pane.write("echo BACK-$((7+7))\r")
        await wait_for(pane, "BACK-14", timeout=15)
        check("Leaves full-screen program cleanly (screen restored)", "Bram Moolenaar" not in screen_text(pane))
        pane.write("vim -u NONE -N\r")
        await wait_for(pane, "~", timeout=15)
        await asyncio.sleep(0.5)
        await pilot.press("escape", "colon", "q", "exclamation_mark", "enter")   # same, through key events
        await asyncio.sleep(1.0)
        pane.write("echo KEYS-$((8+8))\r")
        try:
            await wait_for(pane, "KEYS-16", timeout=10)
            check("Escape and : keys reach vim through key events", True)
        except TimeoutError:
            check("Escape and : keys reach vim through key events", False, "(input mapping to fix)")
            pane.write("\x1b:q!\r")

    async def resize(app, pane, pilot):
        await pilot.resize_terminal(80, 20)
        await asyncio.sleep(0.8)
        pane.write("echo SIZE-$((1+1)) $(tput cols)x$(tput lines)\r")
        await wait_for(pane, "SIZE-2 ")
        text = screen_text(pane)
        got = text[text.find("SIZE-2 "):].split()[1]
        check("Resize reaches the shell", got.startswith("80x"), got + " (a single pane uses the full width)")
        app.save_screenshot(filename="e2e-bash.svg", path=str(OUT))

    await run(BASH, [basics, unicode, throughput, keys, fullscreen, resize])


async def powershell() -> None:
    async def basics(app, pane, pilot):
        pane.write("Write-Output ('PS-READY-' + (6*7))\r")
        t = await wait_for(pane, "PS-READY-42", timeout=40)
        check("PowerShell: command runs", True, f"{t:.2f}s")
    await run("PowerShell", [basics])


async def wsl() -> None:
    async def basics(app, pane, pilot):
        pane.write("echo WSL-$(uname -s)\r")
        t = await wait_for(pane, "WSL-Linux", timeout=60)
        check("WSL bash: command runs", True, f"{t:.2f}s")
    await run("WSL", [basics])


BASH = "Git Bash" if sys.platform == "win32" else "bash"
RUNS = (((BASH, bash), ("PowerShell", powershell), ("WSL", wsl)) if sys.platform == "win32"
        else ((BASH, bash),))


async def main() -> None:
    for name, fn in RUNS:
        print(f"== {name}")
        try:
            await fn()
        except Exception as exc:  # noqa: BLE001 - report every failure and continue
            check(f"{name} run", False, f"{type(exc).__name__}: {str(exc)[:300]}")


asyncio.run(main())
sys.exit(1 if FAILED else 0)
