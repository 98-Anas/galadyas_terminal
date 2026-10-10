# Architecture

For contributors and the curious. The design keeps pure, testable logic separate from the user interface and
from operating-system adapters.

```
                 keys, mouse, paste                         bytes
   ┌──────────┐ ───────────────────▶ ┌──────────────┐ ───────────────▶ ┌───────────────┐
   │ Textual  │                      │ TerminalPane │                  │ PTY adapter   │──▶ shell
   │ App      │ ◀─────────────────── │ (widget.py)  │ ◀─────────────── │ ConPTY / pty  │◀──
   └──────────┘   strips, 30 fps     └──────┬───────┘   reader thread  └───────────────┘
        │                                   │ feed (under a lock)
        │ prefix keys, tabs, splits,        ▼
        │ palette, dialogs           ┌──────────────┐
        │                            │TerminalScreen│ pyte + scrollback, alternate screen,
        ▼                            │ (screen.py)  │ safe replies, clean titles
   task manager, toolkits            └──────────────┘
```

## Modules

| Module | Role | Kind |
|---|---|---|
| `app.py` | Tabs, split layout, prefix commands, palette, status bar, CLI | UI |
| `widget.py` | `TerminalPane`: PTY reader thread, rendering, keys, mouse, paste, copy mode UI | UI |
| `screen.py` | `TerminalScreen`: pyte screen with scrollback, alternate screen, safe replies, title cleaning | core |
| `copymode.py` | Cursor, motions, search and selection over frozen lines | pure |
| `keys.py` | Key event to xterm byte sequence | pure |
| `paste.py` | Sanitising and bracketing pasted text | pure |
| `toolkit.py` | Toolkit data, search, placeholder filling and quoting | pure |
| `aliases.py` | Alias data, bash and PowerShell generators | pure |
| `config.py` | Settings parsing, validation and atomic saving | pure + file |
| `shells.py` | Shell detection and safe program lookup | adapter |
| `pty.py` | ConPTY (pywinpty) on Windows, ptyprocess on Linux, one small interface | adapter |
| `tasks.py` | Process and GPU collection (psutil, nvidia-smi), sorting, filtering | adapter + pure |
| `taskman.py`, `toolkit_screen.py`, `dialogs.py` | Screens and dialogs | UI |
| `theme.py` | Colour palettes | data |

## Data flow and threads

- Each pane starts its shell in a pseudo-terminal and a **reader thread**. The thread reads available output
  without blocking, feeds it to the pane's `TerminalScreen` under a lock, and marks the pane dirty.
- A **30 fps timer** on the UI thread repaints dirty panes. `render_line` builds each row from the screen
  buffer, merging runs of identical style into one segment; styles are cached per theme.
- Keys go the other way: the pane asks the app first (prefix commands), then copy mode, then encodes the key
  for the program.
- **Copy mode** takes a snapshot of scrollback and screen (row copies) so reading never contends with the
  reader thread.
- The **task manager** collects in a worker thread every two seconds and hands results to the UI thread.

## Performance notes

| Measurement (100,000 lines through bash) | Windows (ConPTY, Git Bash) | Linux (WSL 2) |
|---|---|---|
| Throughput | 10,000 to 15,500 lines/s | 56,000 to 80,000 lines/s |

- On Windows, the original high-level pywinpty wrapper delivered output in tiny chunks (934 lines/s). The
  low-level `winpty.PTY` API with non-blocking reads is about fifteen times faster.
- Parsing itself is cheap (about 1.4 s for 100,000 lines); the rest is the operating system's pseudo-terminal
  and process scheduling.
- Collecting processes on Windows: `num_threads`, `status` and `memory_percent` each cost about a second per
  refresh, so they are not collected; memory share is computed from RSS.

## Testing

| Layer | How |
|---|---|
| Pure logic | Plain pytest: copy mode, keys, paste, toolkit, aliases, config, task sorting |
| Screen model | Feeding sequences to `TerminalScreen`, including hostile input |
| App | Textual's `run_test` pilot with a real shell: splits, zoom, tabs, copy mode, paste confirmation, task manager, toolkit insertion |
| End to end | `spike/check.py`: real shells, throughput, Ctrl+C, vim in and out, resize; on Windows (Git Bash, PowerShell, WSL) and Linux |
| Docs | `tools/gen_docs.py --check` keeps the reference pages identical to the code |
| Local CI | `tools/ci.py` runs every gate above plus ruff (with security rules) and pip-audit; `--linux` repeats them on Linux through WSL |

## Design rules

- Nothing runs without the user pressing Enter; nothing destructive without a confirmation.
- No network, no telemetry, no disk writes except the settings file on request.
- Pure functions for anything that can be pure, so it is tested without a terminal.
- New dependencies need a strong reason; each one is a supply-chain risk.
