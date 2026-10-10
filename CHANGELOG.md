# Changelog

All notable changes are listed here. The format follows [Keep a Changelog](https://keepachangelog.com/),
and versions follow [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-10-11

First usable version.

### Added

- Real shells in pseudo-terminals: ConPTY on Windows (Git Bash first, MSYS2, WSL, PowerShell, cmd) and
  POSIX pseudo-terminals on Linux (bash, zsh, fish, sh).
- Tabs and split panes with a tmux-style prefix key (Ctrl+B by default): split right or down, move, zoom,
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
