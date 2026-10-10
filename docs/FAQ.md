# FAQ

**Is it a terminal emulator or a multiplexer?**
Both, in one window: it runs shells in pseudo-terminals (like a terminal emulator) inside another terminal
window, with tabs, splits and copy mode (like tmux). It runs inside Windows Terminal or any Linux terminal.

**Do I still need tmux?**
Locally, usually not. On remote servers, tmux keeps sessions alive when your connection drops, which a local
app cannot do. Use both: tmux on the server, a different prefix here.

**Does it work over SSH?**
Yes. Run `ssh host` in a pane. You can also install mindas terminal on a Linux server and run it there over SSH.

**Is my data sent anywhere?**
No. No telemetry, no network access by the app. See [Security](Security).

**Why Python? Is it fast enough?**
The parser and screen work in Python; the heavy lifting is the operating system's pseudo-terminal. It handles
10,000 to 80,000 lines per second depending on the platform, far more than anyone reads. See [Architecture](Architecture).

**Can I use it for penetration testing?**
For authorised testing, yes: the security toolkit includes scans of systems you own or are permitted to test,
and the terminal itself suits long engagements. It is not built for, and does not help with, unauthorised
access or evasion.

**Can I add commands for my team?**
Yes: toolkits are plain data in `toolkit.py`. Contributions of whole new fields are welcome. Team-specific
private packs are planned.

**Does it support right-to-left text and complex scripts?**
Characters are displayed in logical order without shaping. Full right-to-left support is not planned for this
app.

**macOS?**
Not tested yet. The Linux code path should work; reports are welcome.

**Why is the default prefix Ctrl+B?**
It is tmux's default, so many people already know it. Bash uses Ctrl+B to move back one character: press it
twice to send it, or choose another prefix.

**How do I reset everything?**
Delete the settings file ([Configuration](Configuration)). Nothing else is stored.
