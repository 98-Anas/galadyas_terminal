"""Documentation screenshots, made in a virtual demo environment and checked for personal information.

Usage: uv run python tools/screenshots.py            (writes docs/images/*.png)

- Shells start without profiles, with a neutral prompt (demo@terminal) in a temporary project folder.
- The home window shows a sample system line and a sample list of shells, never this machine's.
- Each SVG is scanned for the real user name, host name and home folder; a match stops the run.
- PNGs are rendered with headless Chrome or Edge, which load the monospace web font the SVG asks for,
  so every character sits in its cell (other converters fall back to proportional fonts and shift text).
"""

from __future__ import annotations

import asyncio
import getpass
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "images"
SIZE = (132, 34)

BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "google-chrome", "chromium", "chromium-browser", "microsoft-edge",
]


def demo_project() -> Path:
    root = Path(tempfile.mkdtemp(prefix="mt-demo-"))
    project = root / "project"
    (project / "src").mkdir(parents=True)
    (project / "data").mkdir()
    for name, text in {"README.md": "# demo\n", "pyproject.toml": "[project]\nname='demo'\n",
                       "Dockerfile": "FROM python:3.12-slim\n", "src/train.py": "print('training')\n",
                       "data/events.csv": "id,value\n1,10\n"}.items():
        (project / name).write_text(text)
    log = [f"[{i:02d}/40] compiling module_{i:02d}.py ... ok" for i in range(1, 39)]
    log += ["[39/40] running tests ... 2 failed", "ERROR: tests/test_api.py::test_timeout - TimeoutError",
            "ERROR: tests/test_api.py::test_retry - ConnectionError", "[40/40] build finished with errors"]
    (project / "build.log").write_text("\n".join(log) + "\n")
    return project


def private_markers() -> list[str]:
    """Strings that must never appear in a published image."""
    marks = {getpass.getuser(), platform.node(), str(Path.home()), Path.home().name}
    marks |= {m.upper() for m in marks} | {m.lower() for m in marks}
    return sorted(m for m in marks if m and len(m) >= 3)


def scan(svg: Path, markers: list[str]) -> None:
    text = svg.read_text(encoding="utf-8").replace("&#160;", " ")
    found = [m for m in markers if m in text]
    if found:
        raise SystemExit(f"{svg.name} contains private information ({len(found)} marker(s)); not published")


def browser() -> str:
    for b in BROWSERS:
        if Path(b).is_file() or shutil.which(b):
            return b
    raise SystemExit("Chrome or Edge is needed to render screenshots")


def render(svg: Path, png: Path, exe: str) -> None:
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg.read_text(encoding="utf-8"))
    w, h = (int(float(m.group(1))), int(float(m.group(2)))) if m else (1700, 1000)
    html = svg.with_suffix(".html")
    # Ligatures off: the web font would draw "!=" as one symbol, which misrepresents a command.
    style = "<style>body{margin:0;background:#0b0f1e} text{font-variant-ligatures:none;font-feature-settings:'liga' 0,'calt' 0}</style>"
    html.write_text(f"<html><head>{style}</head><body>{svg.read_text(encoding='utf-8')}</body></html>", encoding="utf-8")
    subprocess.run([exe, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    f"--window-size={w},{h}", f"--screenshot={png}", html.as_uri()],
                   check=True, capture_output=True, timeout=60)


async def capture(work: Path) -> list[Path]:
    project = demo_project()
    os.environ.update(PS1="demo@terminal:~/project$ ", HOME=str(project.parent), HISTFILE=os.devnull,
                      USER="demo", LOGNAME="demo")
    from galadyas_terminal import home, shells
    from galadyas_terminal.app import GaladyasTerminal
    from galadyas_terminal.config import Settings

    home.system_line = lambda: "Linux  ·  8 CPUs, 16.0 GB RAM"
    found = shells.detect()
    bash = next((s for s in found if "bash" in s.name.lower()), found[0])
    demo_bash = shells.Shell("bash", (bash.argv[0], "--noprofile", "--norc", "-i"))
    sample = [demo_bash, shells.Shell("zsh", ("zsh",)), shells.Shell("WSL: Ubuntu", ("wsl",)),
              shells.Shell("PowerShell 7", ("pwsh",))]
    settings = Settings(remember_history=False)
    app = GaladyasTerminal(demo_bash, available=sample, cwd=str(project), settings=settings)
    shots: list[Path] = []

    def shot(name: str) -> None:
        app.save_screenshot(filename=f"{name}.svg", path=str(work))
        shots.append(work / f"{name}.svg")

    async with app.run_test(size=SIZE) as pilot:
        await asyncio.sleep(1.0)
        shot("home")
        await pilot.press("1")
        await asyncio.sleep(1.5)
        pane = app.current_pane()
        pane.write("ls -p --color=always\r")
        await asyncio.sleep(0.5)
        pane.write("git --version 2>/dev/null | head -1; python --version 2>&1 | head -1\r")
        await asyncio.sleep(1.0)
        shot("single")
        await pilot.press("ctrl+b", "percent_sign")
        await asyncio.sleep(1.5)
        app.current_pane().write("cat build.log\r")
        await asyncio.sleep(1.0)
        shot("splits")
        await pilot.press("ctrl+b")
        await pilot.pause()
        shot("prefix")
        await pilot.press("escape", "ctrl+b", "left_square_bracket", "question_mark", *"error", "enter")
        await asyncio.sleep(0.3)
        shot("copy-mode")
        await pilot.press("q")
        app.history.add("docker compose up -d --build")
        app._ranked = None
        await pilot.press(*"docker co")
        await asyncio.sleep(0.4)
        shot("autocomplete")
        await pilot.press("ctrl+u", "ctrl+b", "g")
        await pilot.pause()
        await pilot.press(*"kubectl")
        await asyncio.sleep(0.5)
        shot("toolkits")
        await pilot.press("escape")
        await pilot.press("ctrl+b", "m")
        await pilot.pause()
        app.screen.show("Getting-Started")
        await asyncio.sleep(0.5)
        shot("manual")
        await pilot.press("escape")
        app.set_option("theme", "light")
        await pilot.press("ctrl+b", "question_mark")
        await pilot.pause()
        shot("help-light")
        app.exit()
    return shots


def main() -> int:
    markers = private_markers()                  # before the demo environment replaces USER and HOME
    work = Path(tempfile.mkdtemp(prefix="mt-shots-"))
    svgs = asyncio.run(capture(work))
    for svg in svgs:
        scan(svg, markers)
    exe = browser()
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.png"):
        old.unlink()
    for svg in svgs:
        render(svg, OUT / f"{svg.stem}.png", exe)
        print(f"wrote {OUT / (svg.stem + '.png')}")
    shutil.rmtree(work, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
