# mindas terminal

![status: work in progress](https://img.shields.io/badge/status-work%20in%20progress-orange)
![license: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue)
![platforms: Windows | Linux](https://img.shields.io/badge/platforms-Windows%20%7C%20Linux-informational)

A universal terminal for Windows and Linux. It runs real shells (bash first, also on Windows through
Git Bash, MSYS2 or WSL) inside a fast text interface built on Textual.

This is an early version. The full documentation and demo arrive with v0.1.

## Install

Requires Python 3.11 or newer. Use [uv](https://docs.astral.sh/uv/) or pipx.

```bash
# from a local clone
uv tool install .
# or
pipx install .
```

Then run:

```bash
mindas-terminal                    # best available shell (bash preferred)
mindas-terminal --list-shells      # shells found on this machine
mindas-terminal --shell powershell
```

Press `Ctrl+Q` to quit.

## Supported shells

| Platform | Detection order |
|---|---|
| Windows | Git Bash, MSYS2 bash, WSL bash, PowerShell 7, Windows PowerShell, cmd |
| Linux | `$SHELL`, bash, zsh, fish, sh |

## Development

```bash
uv sync
uv run pytest
uv run python spike/check.py        # end-to-end checks against real shells
```

## License

Apache-2.0. See [LICENSE](LICENSE).
