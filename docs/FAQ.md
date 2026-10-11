# FAQ

**Is it a terminal emulator or a multiplexer?**
Both, in one window: it runs shells in pseudo-terminals (like a terminal emulator) inside another terminal
window, with tabs, splits and copy mode. It runs inside Windows Terminal or any Linux terminal.

**Does it keep remote sessions alive if my connection drops?**
No. It is a local app. To keep work running on a remote server after a disconnect, use a session manager on
the server, and choose a different prefix key here so the two do not clash.

**Does it work over SSH?**
Yes. Run `ssh host` in a pane. You can also install galadyas terminal on a Linux server and run it there over SSH.

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
It is a widely used default, so many people already know it. Bash uses Ctrl+B to move back one character: press it
twice to send it, or choose another prefix.

**How do I reset everything?**
Delete the settings file ([Configuration](Configuration)). Nothing else is stored.
