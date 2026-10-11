"""The man page (roff), built from the same data as the app so it can never be out of date.

    galadyas-terminal --man | man -l -                     # read it now (Linux)
    galadyas-terminal --man > ~/.local/share/man/man1/galadyas-terminal.1   # install for `man galadyas-terminal`
"""

from __future__ import annotations

from . import __version__, aliases, config, toolkit

RELEASED = "2026-10-11"      # release date of this version; fixed so the generated page is reproducible


def _esc(text: str) -> str:
    """Escape for roff: backslashes, and a leading dot or quote that roff would read as a request."""
    text = text.replace("\\", "\\e").replace("-", "\\-")
    return "\\&" + text if text[:1] in (".", "'") else text


def _tp(term: str, desc: str) -> list[str]:
    return [".TP", f"\\fB{_esc(term)}\\fR", _esc(desc)]


KEYS = [
    ("Tabs", [("prefix c", "new tab"), ("prefix n, prefix p", "next, previous tab"), ("prefix 1..9", "go to tab"),
              ("prefix ,", "rename tab"), ("prefix &", "close tab (asks first)")]),
    ("Panes", [("prefix % or prefix |", "split right"), ('prefix " or prefix -', "split down"),
               ("prefix arrow, prefix h j k l", "move between panes"), ("prefix o", "next pane"),
               ("prefix z", "zoom the pane, toggle"), ("prefix x", "close the pane (asks first)")]),
    ("Copy mode", [("prefix [, Shift+PageUp, mouse wheel", "enter copy mode"),
                   ("h j k l, w b, 0 ^ $, H M L", "move"), ("Ctrl+U, Ctrl+D, Ctrl+B, Ctrl+F", "half page, page"),
                   ("g, G", "oldest, newest line"), ("/ ?, n N", "search forward, backward; next, previous"),
                   ("v, V, y", "select characters, select lines, copy"), ("q, Esc", "leave")]),
    ("Tools", [("prefix H", "home window"), ("prefix g", "toolkits"), ("prefix t", "task manager"),
               ("prefix m", "manual"), ("prefix : or prefix P", "command palette"),
               ("prefix ]", "paste the last copy"), ("prefix ?", "keyboard reference"), ("Ctrl+Q", "quit")]),
]


def render() -> str:
    out = [
        f'.TH GALADYAS\\-TERMINAL 1 "{RELEASED}" "galadyas-terminal {__version__}" "User Commands"',
        ".SH NAME", "galadyas\\-terminal \\- universal terminal for Windows and Linux with tabs, splits, "
        "copy mode, task manager and toolkits",
        ".SH SYNOPSIS", ".B galadyas\\-terminal", "[\\fIOPTIONS\\fR]",
        ".SH DESCRIPTION",
        "Runs real shells (bash first, also on Windows through Git Bash or WSL) in a text interface with tabs "
        "and split panes controlled by a tmux\\-style prefix key, vim\\-style copy mode over the scrollback, a "
        "task manager with GPU use, and offline toolkits of curated commands for eleven fields. Toolkit "
        "commands are typed at the prompt and never run automatically.",
        ".PP", "The prefix key is \\fBCtrl+B\\fR by default: press it, release it, then the command key. "
        "Press it twice to send it to the program.",
        ".SH OPTIONS",
    ]
    options = [
        ("--shell NAME", "shell to start; part of the name is enough (see --list-shells)"),
        ("--list-shells", "list detected shells, best first, and exit"),
        ("--prefix KEY", "prefix key: " + ", ".join(config.PREFIXES)),
        ("--scrollback N", "lines of scrollback per pane, 0 to 1000000 (default 10000)"),
        ("--cwd DIR", "start directory for new shells"),
        ("--profile FIELD", "toolkit field listed first: " + ", ".join(toolkit.FIELDS)),
        ("--theme NAME", "colours: " + ", ".join(config.THEMES)),
        ("--no-home", "start in a shell instead of the home window"),
        ("--aliases bash|powershell|list", "print the opt-in aliases and exit"),
        ("--alias-style linux|native", "include Linux command names in the PowerShell aliases, or not"),
        ("--init-config", "write a settings file with the defaults and exit (never overwrites)"),
        ("--man", "print this manual page in roff format and exit"),
        ("--version", "print the version and exit"),
    ]
    for opt, desc in options:
        out += _tp(opt, desc)
    out.append(".SH KEYS")
    for section, rows in KEYS:
        out += [".SS " + _esc(section)]
        for k, d in rows:
            out += _tp(k, d)
    out += [".SH TOOLKITS",
            f"{len(toolkit.TOOLS)} commands in these fields (profile name, then field):"]
    for key, label in toolkit.FIELDS.items():
        out += _tp(key, label)
    out += [".PP", _esc(toolkit.SECURITY_NOTICE)]
    out += [".SH ALIASES", f"{len(aliases.ALIASES) + len(aliases.LINUX_STYLE)} opt\\-in aliases and helper "
            "functions. Nothing is installed automatically. Try them with:",
            ".PP", ".nf", 'eval "$(galadyas\\-terminal \\-\\-aliases bash)"',
            "galadyas\\-terminal \\-\\-aliases powershell | Out\\-String | Invoke\\-Expression", ".fi"]
    out += [".SH FILES", ".TP", "\\fI%APPDATA%\\\\galadyas\\-terminal\\\\config.toml\\fR (Windows), "
            "\\fI~/.config/galadyas\\-terminal/config.toml\\fR (Linux)",
            "Settings, TOML, read as data only. Keys: " + ", ".join(
                f.name for f in config.fields(config.Settings)) + "."]
    out += [".SH ENVIRONMENT", "Shells start with \\fBTERM=xterm\\-256color\\fR, \\fBCOLORTERM=truecolor\\fR and "
            "\\fBTERM_PROGRAM=galadyas\\-terminal\\fR added to the environment. \\fBXDG_CONFIG_HOME\\fR and "
            "\\fBAPPDATA\\fR locate the settings file."]
    out += [".SH SECURITY", "No network access, no telemetry, scrollback in memory only. Pasted text is "
            "cleaned of control and invisible characters; a paste that would run several commands asks first. "
            "Only fixed\\-format replies are sent to programs. Programs are never looked up in the current folder. "
            "Use the security toolkit only on systems you own or are authorised in writing to test."]
    out += [".SH EXIT STATUS", "0 on success, 1 when no shell is found, 2 for an unknown shell name."]
    out += [".SH SEE ALSO", "\\fBtmux\\fR(1), \\fBvim\\fR(1), \\fBbash\\fR(1). The full manual is inside the app "
            "(prefix m) and at https://github.com/98\\-Anas/galadyas_terminal/wiki"]
    out += [".SH AUTHOR", "Anas Ayman Elgallad."]
    return "\n".join(out) + "\n"
