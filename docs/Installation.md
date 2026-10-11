# Installation

galadyas terminal is a Python application. It runs on **Windows 10 (1809 or newer) and 11**, and on **Linux**
(any distribution with Python 3.11 or newer). macOS is not tested yet.

## Requirements

| | Windows | Linux |
|---|---|---|
| Python | 3.11 or newer | 3.11 or newer |
| Installer | [uv](https://docs.astral.sh/uv/) (recommended) or pipx | uv (recommended) or pipx |
| Shells | Git Bash recommended; also WSL, MSYS2, PowerShell, cmd | bash, zsh, fish or sh |
| Host terminal | Windows Terminal recommended | any modern terminal emulator |
| Optional | NVIDIA driver (GPU columns in the task manager) | NVIDIA driver |

Git Bash comes with [Git for Windows](https://git-scm.com/download/win). With it, the default shell on Windows
is bash, so the commands and habits are the same as on Linux.

## Install with uv (recommended)

### Windows (PowerShell)

```powershell
# 1. Install uv (once)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 2. Install galadyas terminal
uv tool install git+https://github.com/98-Anas/galadyas_terminal

# 3. Run it
galadyas-terminal
```

### Linux

```bash
# 1. Install uv (once)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install galadyas terminal
uv tool install git+https://github.com/98-Anas/galadyas_terminal

# 3. Run it
galadyas-terminal
```

If the command is not found after installing, open a new terminal, or run `uv tool update-shell` once.

## Install with pipx

```bash
pipx install git+https://github.com/98-Anas/galadyas_terminal
```

## Install from a local clone

```bash
git clone https://github.com/98-Anas/galadyas_terminal
cd galadyas_terminal
uv tool install .
```

## Check the installation

```bash
galadyas-terminal --version
galadyas-terminal --list-shells      # the shells it found, best first
```

## Man page

```bash
galadyas-terminal --man | man -l -                                  # read it now
mkdir -p ~/.local/share/man/man1
galadyas-terminal --man > ~/.local/share/man/man1/galadyas-terminal.1 # then: man galadyas-terminal
```

The same page is in the repository at `docs/man/galadyas-terminal.1`. On Windows, read the manual inside the
app instead (`Ctrl+B` then `m`), or with `galadyas-terminal --help`.

## Upgrade and uninstall

```bash
uv tool upgrade galadyas-terminal     # or: uv tool install --force git+https://github.com/98-Anas/galadyas_terminal
uv tool uninstall galadyas-terminal
```

Uninstalling leaves your settings file. Delete it yourself if you want a clean slate; see
[Configuration](Configuration) for its location.

## Offline and restricted machines

Build a wheel on a connected machine and copy it:

```bash
uv build                                   # creates dist/galadyas_terminal-<version>-py3-none-any.whl
uv tool install dist/galadyas_terminal-*.whl # on the target machine (dependencies must be available)
```

On university or company HPC login nodes without admin rights, uv and pipx install into your home folder,
so no administrator is needed.

## Verifying what you install

The source is public. Dependencies are pinned in `uv.lock` and checked for known vulnerabilities with
`pip-audit`. See [Security](Security).
