"""Generate the reference pages from the code, so the documentation can never drift from the app.

Usage: uv run python tools/gen_docs.py        (tests fail if the committed pages are out of date)
"""

from __future__ import annotations

import sys
from pathlib import Path

from galadyas_terminal import aliases, manpage, toolkit

DOCS = Path(__file__).resolve().parent.parent / "docs"


def _cell(text: str) -> str:
    return text.replace("|", "\\|")


def toolkits_page() -> str:
    out = ["# Toolkit Reference", "",
           "Generated from `src/galadyas_terminal/toolkit.py`. Open the toolkits with `prefix g` "
           "(or `Toolkits` in the command palette), type a few words, press Enter.", "",
           "Commands are **inserted at the prompt and never run**. Values you type for `<placeholders>` are "
           "quoted so they stay one argument. Platform `any` means both Windows (Git Bash or PowerShell) and Linux.",
           "", f"> **Ethical use.** {toolkit.SECURITY_NOTICE}", "",
           f"{len(toolkit.TOOLS)} commands in {len(toolkit.FIELDS)} fields.", ""]
    out += ["| Field | Profile name |", "|---|---|"]
    out += [f"| [{label}](#{key}) | `{key}` |" for key, label in toolkit.FIELDS.items()]
    for key, label in toolkit.FIELDS.items():
        out += ["", f'<a id="{key}"></a>', "", f"## {label}", "", "| Task | Command | Platform |", "|---|---|---|"]
        for t in (t for t in toolkit.TOOLS if t.field == key):
            note = f"<br><sub>{_cell(t.note)}</sub>" if t.note and t.note != toolkit.SECURITY_NOTICE else ""
            out.append(f"| {_cell(t.title)}{note} | `{_cell(t.command)}` | {t.platform} |")
    return "\n".join(out) + "\n"


def aliases_page() -> str:
    out = ["# Aliases Reference", "",
           "Generated from `src/galadyas_terminal/aliases.py`. These are **opt-in**: nothing changes in your "
           "shell until you add them yourself.", "",
           "```bash", "# bash or zsh: try them in the current shell", 'eval "$(galadyas-terminal --aliases bash)"',
           "# keep them: add the same line to ~/.bashrc or ~/.zshrc", "```", "",
           "```powershell", "# PowerShell: try them in the current session",
           "galadyas-terminal --aliases powershell | Out-String | Invoke-Expression",
           "# keep them: add the same line to $PROFILE", "```", "",
           "`--alias-style linux` (default) also gives PowerShell the Linux command names in the first table, "
           "so the same muscle memory works everywhere. `--alias-style native` leaves them out. "
           "Type `malias` in bash to list everything.", "",
           f"{len(aliases.ALIASES) + len(aliases.LINUX_STYLE)} aliases and helper functions.", ""]
    for g in aliases.GROUPS:
        items = [a for a in aliases.ALIASES + aliases.LINUX_STYLE if a.group == g]
        title = "Linux command names in PowerShell" if g == "linux" else g.capitalize()
        out += [f"## {title}", "", "| Name | What it does | bash | PowerShell |", "|---|---|---|---|"]
        for a in items:
            out.append(f"| `{a.name}` | {_cell(a.help)} | {'yes' if a.bash else 'built in'} | "
                       f"{'yes' if a.powershell else 'no'} |")
        out.append("")
    return "\n".join(out)


PAGES = {"Toolkit-Reference.md": toolkits_page, "Aliases-Reference.md": aliases_page,
         "man/galadyas-terminal.1": manpage.render}


def main(check: bool = False) -> int:
    stale = []
    for name, build in PAGES.items():
        path = DOCS / name
        text = build()
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                stale.append(name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")
            print(f"wrote {path}")
    if stale:
        print("out of date: " + ", ".join(stale) + " (run: uv run python tools/gen_docs.py)")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(check="--check" in sys.argv))
