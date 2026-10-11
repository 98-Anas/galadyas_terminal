# Troubleshooting

## `galadyas-terminal` is not found after installing

Open a new terminal. If it is still missing, run `uv tool update-shell` (or `pipx ensurepath`) once, then open
a new terminal. The command lives in `~/.local/bin` (Linux) or `%USERPROFILE%\.local\bin` (Windows).

## It opens PowerShell, but I want bash on Windows

Install [Git for Windows](https://git-scm.com/download/win), then check `galadyas-terminal --list-shells`.
Git Bash is found in `C:\Program Files\Git`. For WSL, install a distribution with `wsl --install`.
To choose explicitly: `galadyas-terminal --shell "git bash"` or `shell = "Git Bash"` in the settings file.

## Keys do nothing or do something else

- Some host terminals take keys for themselves. In the VS Code terminal, Ctrl+P, Ctrl+B and others may go to
  VS Code: use Windows Terminal, or change the prefix (`--prefix ctrl+a`), or adjust VS Code's
  `terminal.integrated.commandsToSkipShell`.
- `Ctrl+Q` quits the app, so programs never receive it.
- After pressing the prefix, the next key is a terminal command. Press the prefix twice to send it to the program.

## Colours look wrong or dull

Use a host terminal with true colour (Windows Terminal, most Linux terminals). Programs inside see
`TERM=xterm-256color` and `COLORTERM=truecolor`. Try `--theme contrast` for maximum readability.

## Copying does not reach the system clipboard

The system clipboard is set through the host terminal (OSC 52). Windows Terminal supports it. Some Linux
terminals need it enabled, and tmux needs `set -g set-clipboard on`. Inside galadyas terminal, `prefix ]` pastes
the last copy regardless.

## A paste asks for confirmation every time

That happens when the shell has not enabled bracketed paste and the text has several lines, because each line
would run at once. Bash 5.1+ and PowerShell 7 enable bracketed paste. To turn the question off (not
recommended), set `confirm_multiline_paste = false`.

## Output on Windows is slower than on Linux

Windows pseudo-terminals (ConPTY) are slower than Linux ones; see [Architecture](Architecture) for numbers.
For very large outputs, redirect to a file (`command > out.txt`) and open it with `less`.

## The task manager shows no GPU

It needs `nvidia-smi` from the NVIDIA driver in a `PATH` folder. On Windows with WDDM drivers, per-process GPU
memory may be unavailable while the totals still show. Other GPU vendors are not supported yet.

## A full-screen program left the screen messy

Press `Ctrl+L` (most shells redraw) or run `reset`. If you can reproduce it, please report the program and the
steps.

## Warnings about the settings file on start-up

The message names the setting. Fix or remove it; the default is used meanwhile. Run
`galadyas-terminal --init-config` on a fresh system to get a valid file.

## Reporting a bug

Open an issue with: `galadyas-terminal --version`, your operating system, the shell, the host terminal, what
you did, what you expected, and what happened. For security problems, see [Security](Security) instead.
