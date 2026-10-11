# Changelog

All notable changes are listed here. The format follows [Keep a Changelog](https://keepachangelog.com/),
and versions follow [Semantic Versioning](https://semver.org/).

## [0.4.0] - 2026-10-11

galadyas_terminal is the new name of this project, part of the galadyas series of open projects.

### Changed

- Project, package and command renamed from mindas_terminal / `mindas-terminal` to galadyas_terminal /
  `galadyas-terminal`. The repository moved to github.com/98-Anas/galadyas_terminal; the old address redirects.
- Settings now live in a `galadyas-terminal` folder. On first start your existing `mindas-terminal` settings
  are copied over automatically.

### Deprecated

- The `mindas-terminal` command still works as an alias and will be removed in a later release.

## [0.3.0] - 2026-10-11

A cleaner, calmer interface, shaped by how people work in the terminal every day.

### Changed

- Status bar shows the mode (NORMAL, PREFIX, COPY, ZOOM) and the keys that work right now, as clickable key
  chips. It replaces the fixed word list and the CPU and RAM readout.
- A tab with one pane shows it without a border, like a plain terminal; borders appear when you split.
- Compact one-line tab bar.
- Home window: simple title, no host name, calmer focus style.
- Screenshots rendered with a real browser engine, so text and borders align exactly, from a demo
  environment checked for personal information (`tools/screenshots.py`).

## [0.2.0] - 2026-10-11

Smarter, smoother, still simple: nothing new to learn.

### Added

- Autocomplete: a faint suggestion appears after what you type, from your own history (frequent and recent
  first), common tools and toolkit commands. Right arrow or End accepts it, Alt+Right accepts one word.
- "Did you mean": after `command not found`, the closest known command is offered on the empty prompt;
  Right arrow accepts it.
- Remembered history for autocomplete, with secret filtering, private file permissions, a
  `remember_history` setting and a *Forget history* command.
- Autocomplete page in the manual and the wiki.

### Changed

- Smoother rendering: only the rows that changed are repainted, which keeps many panes fluid.
- Screenshots now come from a neutral demo environment.

## [0.1.0] - 2026-10-11

First usable version.

### Added

- Real shells in pseudo-terminals: ConPTY on Windows (Git Bash first, MSYS2, WSL, PowerShell, cmd) and
  POSIX pseudo-terminals on Linux (bash, zsh, fish, sh).
- Tabs and split panes with a prefix key (Ctrl+B by default): split right or down, move, zoom,
  rename, close with confirmation.
- Scrollback (10,000 lines per pane by default) and vim-style copy mode with motions, smartcase search,
  character and line selection, clipboard and an internal paste buffer.
- Alternate screen support: vim, less, htop and similar programs restore the shell screen on exit.
- Task manager: CPU, memory and NVIDIA GPU per process, sorting, filtering, an only-this-terminal view,
  terminate and kill with confirmation.
- Toolkits: 109 curated commands for 11 fields with search, profiles and safe placeholder filling.
  Commands are inserted, never run.
- 89 opt-in aliases and helper functions for bash and PowerShell, including Linux command names for
  PowerShell (`alias_style`).
- Settings file (TOML), command-line options, command palette switches for shell, profile, theme and prefix.
- Themes: space, light and high contrast.
- Home window with clickable cards for every shell (each WSL distribution by name) and tool.
- Clickable status-bar actions; mouse support for tabs, panes, dialogs and the manual.
- Manual inside the app (offline, searchable, linked pages) and a man page (`--man`, `docs/man`).
- Documentation and wiki pages, with reference pages generated from the code.

### Security

- Paste sanitising (control and invisible format characters removed), bracketed paste, confirmation for
  multi-line pastes that would run.
- Only fixed-format replies to terminal queries; titles sanitised; clipboard writes from output ignored.
- Program lookup that never uses the current folder (prevents binary planting on Windows).
- Bounded scrollback; tolerant parser that recovers from malformed input.
