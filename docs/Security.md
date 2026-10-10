# Security

A terminal sees passwords, keys and production systems. This page describes what mindas terminal protects
against, how, and what remains your responsibility.

## Ethical use

mindas terminal is built for people who protect, operate, research and learn: engineers, administrators,
analysts, students and authorised security testers. The security toolkit covers defence and authorised
testing only. **Use it only on systems you own or are authorised in writing to test.** Unauthorised scanning
or access is illegal in most countries. The project does not accept contributions whose purpose is to attack
systems without consent, evade detection, or harm people.

## What the app does not do

- **No network access.** The app itself opens no connections. (Commands you run, and the `myip` alias, are
  yours.)
- **No telemetry**, no analytics, no update checks.
- **No disk logging.** Scrollback and the copy buffer live in memory and vanish when the pane closes. The
  only file the app writes is the settings file, and only when you choose *Save settings* or `--init-config`.
- **No automatic changes to your shell.** Aliases are printed for you to review and add yourself.
- **No commands run on your behalf.** Toolkit commands are inserted at the prompt; you press Enter.

## Threats and protections

| Threat | Protection | Tested in |
|---|---|---|
| **Paste injection**: a web page hides a newline or escape sequence in text you copy | Control and invisible format characters (including bidi overrides) are removed; bracketed paste is used when the shell supports it; otherwise a multi-line paste shows the lines and asks first, with *Cancel* focused | `tests/test_paste.py`, `tests/test_app.py` |
| **Bracketed-paste escape**: pasted text containing `ESC[201~` to end the bracket early | Escape characters are removed before wrapping | `tests/test_paste.py` |
| **Answer-back attacks**: output (for example a file you `cat`) asks the terminal to reply, and the reply is typed into your shell | Only fixed-format replies are sent: cursor position, device attributes and status OK, which contain no attacker-controlled text. Title reports, clipboard reads and unknown queries are never answered | `tests/test_screen.py` |
| **Title injection**: a program sets a title containing escape sequences | Titles keep printable characters only, at most 60 | `tests/test_screen.py` |
| **Clipboard writes from output (OSC 52)** | Ignored; only copy mode writes the clipboard, on your key press | `tests/test_screen.py` |
| **Malformed or hostile sequences** crashing or freezing the terminal | The parser tolerates unknown sequences; if parsing fails, it resets and the pane keeps working. Huge parameters are clamped | `tests/test_screen.py` |
| **Memory exhaustion** from endless output | Scrollback is bounded (10,000 lines by default, at most 1,000,000) | `tests/test_screen.py` |
| **Binary planting**: a `nvidia-smi.exe` or `wsl.exe` placed in a repository you open | Programs are found only in absolute `PATH` folders, never the current folder (Windows searches it first by default) | `tests/test_shells.py` |
| **Shell injection through toolkit values** | Values are stripped of control characters and quoted as one argument; inside existing quotes, closing characters are removed | `tests/test_toolkit.py` |
| **Accidental process termination** | Confirmation with the full command line; system processes and the app itself are refused | `tests/test_tasks.py` |
| **Malicious settings file** | TOML is parsed as data; unknown keys, wrong types and out-of-range values are ignored | `tests/test_config.py` |
| **Weak generated passwords** | `genpass` uses cryptographic randomness on both shells | `docs/Aliases.md` |
| **Vulnerable dependencies** | Few dependencies (Textual, pyte, psutil, pywinpty or ptyprocess), versions locked in `uv.lock`, checked with `pip-audit` | local CI (`tools/ci.py`) |

## What remains your responsibility

- Programs you run in the terminal have your permissions. The terminal cannot make an unsafe command safe.
- Copy mode puts text on the system clipboard, where other applications can read it. Avoid copying secrets.
- Screen contents may include secrets; lock your screen when you leave.
- If you add aliases to your profile, they run as you; read them first (`mindas-terminal --aliases bash | less`).
- Turning off `confirm_multiline_paste` removes a protection; keep it on unless you understand the risk.

## Supported versions

| Version | Security fixes |
|---|---|
| 0.1.x | Yes |
| older | No |

## Reporting a vulnerability

Please **do not open a public issue** for security problems. Use GitHub's private vulnerability reporting
(*Security* tab, *Report a vulnerability*) on the
[repository](https://github.com/98-Anas/mindas_terminal/security). Include steps to reproduce, the version
(`mindas-terminal --version`), your platform and shell.

You will get an acknowledgement within 7 days. Fixes are released as soon as they are ready, and reporters
are credited in the changelog unless they prefer not to be.
