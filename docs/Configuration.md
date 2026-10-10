# Configuration

Settings come from three places, in this order (later wins):

1. Built-in defaults
2. The settings file
3. Command-line options

You can also change most settings while the app runs, from the command palette (`prefix :`), and keep them
with *Save settings*.

## The settings file

| Platform | Location |
|---|---|
| Windows | `%APPDATA%\mindas-terminal\config.toml` |
| Linux | `$XDG_CONFIG_HOME/mindas-terminal/config.toml` (usually `~/.config/mindas-terminal/config.toml`) |

Create it with the defaults:

```bash
mindas-terminal --init-config
```

Example:

```toml
# mindas-terminal settings. Data only.
shell = "Git Bash"              # a name from --list-shells; empty = best found (bash first)
prefix = "ctrl+a"               # ctrl+b (default), ctrl+a, ctrl+space, ctrl+backslash
scrollback = 20000              # lines kept per pane, 0 to 1000000
profile = "hpc"                 # toolkit field listed first; empty = none
theme = "space"                 # space, light, contrast
alias_style = "linux"           # linux or native (PowerShell aliases)
confirm_multiline_paste = true  # ask before a paste that would run several commands
```

The file is read as **data only** (TOML); it can never run code. Unknown keys, wrong types and invalid values
are ignored with a warning on start-up, and the default is used. A broken file never stops the app.
*Save settings* writes the file atomically, so a crash cannot leave it half-written.

## Command-line options

| Option | Meaning |
|---|---|
| `--shell NAME` | Shell for this run (part of the name is enough: `--shell power`) |
| `--list-shells` | Show detected shells and exit |
| `--prefix KEY` | Prefix key, for example `ctrl+a` |
| `--scrollback N` | Lines of scrollback per pane |
| `--cwd DIR` | Start directory for new shells |
| `--profile FIELD` | Toolkit field listed first |
| `--theme NAME` | `space`, `light` or `contrast` |
| `--aliases bash\|powershell\|list` | Print the opt-in aliases and exit |
| `--alias-style linux\|native` | PowerShell alias flavour for `--aliases powershell` |
| `--init-config` | Write the settings file with defaults (never overwrites) and exit |
| `--version` | Show the version |

## Themes

| Theme | For |
|---|---|
| `space` | Default: dark navy with blue, violet and teal accents |
| `light` | Bright rooms and printing screenshots |
| `contrast` | High contrast: white on black with pure accent colours, for low vision or projectors |

Programs keep their own colours (ls, git, vim); the theme sets the default background and text, borders,
dialogs and the status bar.

## Shell detection

| Platform | Order |
|---|---|
| Windows | Git Bash, MSYS2 bash, WSL bash (default distribution), each WSL distribution by name, PowerShell 7, Windows PowerShell, cmd |
| Linux | `$SHELL`, bash, zsh, fish, sh |

Programs are looked up only in absolute `PATH` folders, never in the current folder (see [Security](Security)).

## Environment for shells

Each shell starts with your environment plus:

| Variable | Value | Why |
|---|---|---|
| `TERM` | `xterm-256color` | Programs use colours and the right keys |
| `COLORTERM` | `truecolor` | Programs may use 24-bit colour |
| `TERM_PROGRAM` | `mindas-terminal` | Scripts can tell where they run |

In your `.bashrc` you can check `[ "$TERM_PROGRAM" = mindas-terminal ]` to set things only inside this app.
