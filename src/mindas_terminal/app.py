"""mindas terminal: tabs and split panes running real shells, with tmux-style keys and vim-style copy mode."""

from __future__ import annotations

import argparse
import sys
import time
from functools import partial

from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.command import DiscoveryHit, Hit, Hits, Provider
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, TabbedContent, TabPane

from . import __version__, aliases, config, paste, shells, suggest, theme, toolkit
from .dialogs import Confirm, Help, Prompt
from .widget import TerminalPane

HELP = """\
Prefix key: {prefix}  (press it, release, then the command key; press it twice to send it to the shell)

Tabs                                  Panes
  prefix c      new tab                 prefix %  |   split right
  prefix n / p  next / previous tab     prefix "  -   split down
  prefix 1..9   go to tab               prefix arrows or h j k l   move between panes
  prefix ,      rename tab              prefix o      next pane
  prefix &      close tab               prefix z      zoom pane (toggle)
                                        prefix x      close pane

Autocomplete: type two or more characters; a faint suggestion appears after the cursor.
  Right arrow or End accepts it, Alt+Right accepts one word, keep typing to ignore it.
  After "command not found", the suggested fix appears on the empty line: Right arrow to use it.

Copy mode (vim keys)                  Tools
  prefix [  or Shift+PageUp  or wheel   prefix t      task manager
  h j k l  w b  0 ^ $  H M L            prefix :  or prefix P   command palette
  Ctrl+U / Ctrl+D  half page            prefix ]      paste the last copied text
  Ctrl+B / Ctrl+F  page, g / G  ends    prefix g      toolkits: commands for your field
                                        prefix H      home window
                                        prefix m      manual (offline, searchable)
                                        prefix ?      this help
  / ?  search,  n / N  next / previous  Ctrl+Q        quit
  v  select, V  select lines, y  copy
  q  or  Esc  leave copy mode

Task manager: c m g p n sort (again to reverse), / filter, f only this terminal,
k terminate, K kill (both ask first), q close.

Safety: multi-line pastes that would run immediately ask first; pasted control characters and invisible
format characters are removed; program titles are sanitised; scrollback stays in memory only; no network
access and no telemetry.
"""

# Clickable words in the status bar; each runs an app action.
STATUS_ACTIONS = ("[@click=app.home]home[/]  [@click=app.new_tab]+tab[/]  [@click=app.split('right')]split[/]  "
                  "[@click=app.zoom]zoom[/]  [@click=app.toolkit]tools[/]  [@click=app.task_manager]tasks[/]  "
                  "[@click=app.manual]manual[/]  [@click=app.help]keys[/]   ")

KEY_NAMES = {"ctrl+b": "Ctrl+B", "ctrl+a": "Ctrl+A", "ctrl+space": "Ctrl+Space", "ctrl+backslash": "Ctrl+\\"}


class TerminalCommands(Provider):
    """Command palette entries: every action plus a new tab for each detected shell."""

    def _commands(self):
        app: MindasTerminal = self.app  # type: ignore[assignment]
        items = [
            ("New tab", app.action_new_tab, "Open a tab with the default shell"),
            ("Split right", partial(app.action_split, "right"), "Split the current pane side by side"),
            ("Split down", partial(app.action_split, "down"), "Split the current pane top and bottom"),
            ("Close pane", app.action_close_pane, "Close the current pane (asks first)"),
            ("Zoom pane", app.action_zoom, "Show only the current pane, toggle"),
            ("Rename tab", app.action_rename_tab, "Give the current tab a name"),
            ("Copy mode", app.action_copy_mode, "Scroll back, search and copy with vim keys"),
            ("Task manager", app.action_task_manager, "Processes, CPU, memory and GPU"),
            ("Toolkits", app.action_toolkit, "Curated commands for DevOps, HPC, AI, data, security, IT, PM"),
            ("Keyboard help", app.action_help, "All key bindings"),
            ("Home window", app.action_home, "Start screen: shells and tools"),
            ("Manual", app.action_manual, "The full manual, offline and searchable"),
            ("Forget history", app.action_forget_history, "Delete remembered commands used for autocomplete"),
            ("Quit", app.action_quit_app, "Close every tab and exit"),
        ]
        for sh in app.shells:
            items.append((f"New tab: {sh.name}", partial(app.action_new_tab, sh), " ".join(sh.argv)))
            items.append((f"Default shell: {sh.name}", partial(app.set_option, "shell", sh.name),
                          "Shell for new tabs and panes"))
        for key, label in toolkit.FIELDS.items():
            items.append((f"Profile: {label}", partial(app.set_option, "profile", key),
                          "List this field's commands first in Toolkits"))
        for name in config.THEMES:
            items.append((f"Theme: {name}", partial(app.set_option, "theme", name), "Switch colours now"))
        for key in config.PREFIXES:
            items.append((f"Prefix key: {KEY_NAMES.get(key, key)}", partial(app.set_option, "prefix", key),
                          "Key that starts tab and pane commands"))
        items.append(("Save settings", app.action_save_settings, str(config.path())))
        return items

    async def discover(self) -> Hits:
        for name, cb, help_text in self._commands():
            yield DiscoveryHit(name, cb, help=help_text)

    async def search(self, query: str) -> Hits:
        matcher = self.matcher(query)
        for name, cb, help_text in self._commands():
            if (score := matcher.match(name)) > 0:
                yield Hit(score, matcher.highlight(name), cb, help=help_text)


class MindasTerminal(App[None]):
    TITLE = "mindas terminal"
    COMMANDS = {TerminalCommands}
    CSS = """
    Screen { layers: base; }
    #tabs { height: 1fr; }
    #tabs > ContentSwitcher { height: 1fr; }
    TabPane { padding: 0; height: 1fr; }
    .columns { height: 1fr; }
    .column { width: 1fr; height: 1fr; }
    #status { height: 1; background: $panel; }
    #status-left { width: 1fr; }
    #status-actions { width: auto; color: $text-muted; }
    #status-right { width: auto; color: $text-muted; }
    """
    BINDINGS = [Binding("ctrl+q", "quit_app", "Quit", priority=True, show=False)]

    def __init__(self, shell: shells.Shell, prefix: str = "ctrl+b", scrollback: int = 10_000,
                 cwd: str | None = None, available: list[shells.Shell] | None = None,
                 profile: str | None = None, settings: config.Settings | None = None) -> None:
        super().__init__()
        self.settings = settings or config.Settings()
        self.shell = shell
        self.shells = available or [shell]
        self.prefix = prefix
        self.scrollback = scrollback
        self.cwd = cwd
        self.profile = profile or self.settings.profile or None
        self.paste_buffer = ""
        self._prefix_armed = False
        self._tab_seq = 0
        self._pane_seq = 0
        self._named: dict[str, str] = {}               # tab id -> user-given name
        self._last_pane: dict[str, TerminalPane] = {}  # tab id -> last focused pane
        self._zoomed: TerminalPane | None = None
        self._sys = ""
        self.history = self._load_history()
        self._ranked: list[str] | None = None
        self._unsaved = 0
        self._extra = tuple(t.command for t in toolkit.for_platform(sys.platform) if "<" not in t.command)

    # layout
    def compose(self) -> ComposeResult:
        yield TabbedContent(id="tabs")
        with Horizontal(id="status"):
            yield Static(id="status-left")
            yield Static(STATUS_ACTIONS, id="status-actions")
            yield Static(id="status-right")

    async def on_mount(self) -> None:
        theme.apply(self, self.settings.theme)
        if self.settings.show_home:
            self.action_home()
        else:
            await self.action_new_tab()
        self._update_system()
        self.set_interval(2.0, self._update_system)

    # autocomplete data
    def _load_history(self) -> suggest.History:
        if not self.settings.remember_history:
            return suggest.History()
        try:
            return suggest.History.loads(config.history_path().read_text(encoding="utf-8"))
        except OSError:
            return suggest.History()

    def save_history(self) -> None:
        if self.settings.remember_history and self._unsaved:
            try:
                config.save_private(config.history_path(), self.history.dumps())
                self._unsaved = 0
            except OSError:
                pass                                   # history is a convenience, never an error

    def remember(self, command: str) -> None:
        if self.history.add(command):
            self._ranked = None
            self._unsaved += 1
            if self._unsaved >= 10:
                self.save_history()

    def completions(self) -> tuple[list[str], tuple[str, ...]]:
        if self._ranked is None:
            self._ranked = self.history.ranked()
        return self._ranked, self._extra

    def action_forget_history(self) -> None:
        def done(ok: bool) -> None:
            if ok:
                self.history = suggest.History()
                self._ranked, self._unsaved = None, 0
                try:
                    config.history_path().unlink(missing_ok=True)
                except OSError:
                    pass
                self.notify("History forgotten", timeout=3)

        self.push_screen(Confirm("Forget all remembered commands?", "Autocomplete starts fresh.", "Forget"), done)

    def exit(self, *args, **kwargs) -> None:
        self.save_history()
        super().exit(*args, **kwargs)

    def action_home(self) -> None:
        from .home import HomeScreen

        def chosen(shell: shells.Shell | None) -> None:
            self.run_worker(self.action_new_tab(shell or self.shell))

        self.push_screen(HomeScreen(self.shells, self.profile), chosen)

    def action_manual(self, page: str = "Home") -> None:
        from .manual import ManualScreen

        self.push_screen(ManualScreen(page))

    def _new_pane(self, shell: shells.Shell | None = None) -> TerminalPane:
        self._pane_seq += 1
        return TerminalPane(shell or self.shell, scrollback=self.scrollback, cwd=self.cwd, id=f"pane-{self._pane_seq}")

    @property
    def tabbed(self) -> TabbedContent:
        return self.query_one("#tabs", TabbedContent)

    def current_pane(self) -> TerminalPane | None:
        if isinstance(self.focused, TerminalPane):
            return self.focused
        tab = self.tabbed.active
        pane = self._last_pane.get(tab)
        if pane is not None and pane.is_attached:
            return pane
        panes = self._tab_panes(tab)
        return panes[0] if panes else None

    def _tab_panes(self, tab_id: str | None) -> list[TerminalPane]:
        if not tab_id:
            return []
        try:
            return list(self.tabbed.get_pane(tab_id).query(TerminalPane))
        except Exception:  # noqa: BLE001 - tab already removed
            return []

    def _grid(self, pane: TerminalPane) -> list[list[TerminalPane]]:
        columns = pane.parent.parent
        return [list(col.query(TerminalPane)) for col in columns.children]

    def all_panes(self) -> list[TerminalPane]:
        return list(self.query(TerminalPane))

    def pane_pids(self) -> set[int]:
        return {p.pid for p in self.all_panes() if p.pid}

    # actions: tabs
    async def action_new_tab(self, shell: shells.Shell | None = None) -> None:
        self._tab_seq += 1
        tab_id = f"tab-{self._tab_seq}"
        pane = self._new_pane(shell)
        body = Horizontal(Vertical(pane, classes="column"), classes="columns")
        await self.tabbed.add_pane(TabPane(self._label(tab_id, pane), body, id=tab_id))
        self.tabbed.active = tab_id
        pane.focus()

    def _tab_ids(self) -> list[str]:
        return [p.id for p in self.tabbed.query(TabPane) if p.id]

    def action_select_tab(self, index: int) -> None:
        ids = self._tab_ids()
        if 0 <= index < len(ids):
            self.tabbed.active = ids[index]

    def action_cycle_tab(self, step: int) -> None:
        ids = self._tab_ids()
        if ids and self.tabbed.active in ids:
            self.tabbed.active = ids[(ids.index(self.tabbed.active) + step) % len(ids)]

    def action_rename_tab(self) -> None:
        tab = self.tabbed.active
        if not tab:
            return

        def done(name: str | None) -> None:
            if name is None:
                return
            if name.strip():
                self._named[tab] = name.strip()[:40]
            else:
                self._named.pop(tab, None)
            self._refresh_labels()

        self.push_screen(Prompt("Rename tab (empty to use the program title)", self._named.get(tab, "")), done)

    def action_close_tab(self) -> None:
        tab = self.tabbed.active
        panes = self._tab_panes(tab)

        async def done(ok: bool) -> None:
            if ok:
                for p in panes:
                    await self._close(p)

        self.push_screen(Confirm(f"Close this tab and its {len(panes)} pane(s)?", ok="Close"), done)

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        tab = event.pane.id
        pane = self._last_pane.get(tab)
        if pane is None or not pane.is_attached:
            panes = self._tab_panes(tab)
            pane = panes[0] if panes else None
        if pane:
            self.call_after_refresh(pane.focus)
        self._refresh_status()

    # actions: panes
    async def action_split(self, direction: str = "right") -> None:
        pane = self.current_pane()
        if pane is None:
            return
        self._unzoom()
        new = self._new_pane(pane.shell)
        if direction == "right":
            await pane.parent.parent.mount(Vertical(new, classes="column"), after=pane.parent)
        else:
            await pane.parent.mount(new, after=pane)
        new.focus()

    def action_focus(self, direction: str) -> None:
        pane = self.current_pane()
        if pane is None or self._zoomed:
            return
        grid = self._grid(pane)
        ci = next(i for i, col in enumerate(grid) if pane in col)
        ri = grid[ci].index(pane)
        if direction in ("left", "right"):
            ci += -1 if direction == "left" else 1
            if not 0 <= ci < len(grid):
                return
            target = grid[ci][min(ri, len(grid[ci]) - 1)]
        else:
            ri += -1 if direction == "up" else 1
            if not 0 <= ri < len(grid[ci]):
                return
            target = grid[ci][ri]
        target.focus()

    def action_next_pane(self) -> None:
        pane = self.current_pane()
        if pane is None or self._zoomed:
            return
        order = [p for col in self._grid(pane) for p in col]
        order[(order.index(pane) + 1) % len(order)].focus()

    def action_zoom(self) -> None:
        pane = self.current_pane()
        if pane is None:
            return
        if self._zoomed:
            self._unzoom()
        else:
            self._zoomed = pane
            for col in pane.parent.parent.children:
                col.display = col is pane.parent
            for p in pane.parent.query(TerminalPane):
                p.display = p is pane
        pane.focus()
        self._refresh_status()

    def _unzoom(self) -> None:
        if self._zoomed and self._zoomed.is_attached:
            for col in self._zoomed.parent.parent.children:
                col.display = True
                for p in col.query(TerminalPane):
                    p.display = True
        self._zoomed = None

    def action_close_pane(self) -> None:
        pane = self.current_pane()
        if pane is None:
            return

        async def done(ok: bool) -> None:
            if ok:
                await self._close(pane)

        self.push_screen(Confirm(f"Close pane '{pane.title}'? Its shell and programs will end.", ok="Close"), done)

    async def _close(self, pane: TerminalPane) -> None:
        if not pane.is_attached:
            return
        if self._zoomed is pane:
            self._unzoom()
        column = pane.parent
        columns = column.parent
        tab = next((a for a in pane.ancestors if isinstance(a, TabPane)), None)
        pane.shutdown()
        await pane.remove()
        if not column.children:
            await column.remove()
        if tab is not None and not columns.children:
            self._named.pop(tab.id, None)
            self._last_pane.pop(tab.id, None)
            await self.tabbed.remove_pane(tab.id)
        if not self.all_panes():
            self.exit()
            return
        nxt = self.current_pane()
        if nxt:
            nxt.focus()
        self._refresh_labels()

    async def on_terminal_pane_exited(self, message: TerminalPane.Exited) -> None:
        await self._close(message.pane)

    def on_terminal_pane_changed(self, message: TerminalPane.Changed) -> None:
        self._refresh_labels()

    def on_descendant_focus(self, event) -> None:
        widget = event.widget
        if isinstance(widget, TerminalPane):
            tab = next((a for a in widget.ancestors if isinstance(a, TabPane)), None)
            if tab is not None:
                self._last_pane[tab.id] = widget
            self._refresh_labels()

    # actions: tools
    def action_copy_mode(self) -> None:
        pane = self.current_pane()
        if pane:
            pane.enter_copy()

    def action_paste_buffer(self) -> None:
        pane = self.current_pane()
        if pane and self.paste_buffer:
            pane.paste_text(self.paste_buffer)

    def action_task_manager(self) -> None:
        from .taskman import TaskManager

        self.push_screen(TaskManager(self.pane_pids))

    def action_toolkit(self) -> None:
        from .toolkit_screen import ToolkitScreen

        pane = self.current_pane()

        def insert(command: str | None) -> None:
            if not command:
                return
            line = paste.sanitize(command).replace("\n", " ")
            if pane is not None and pane.is_attached:
                pane.write(line)                                           # inserted, never run
                pane.focus()
            else:                                                          # opened from the home window
                self.copy_to_clipboard(line)
                self.paste_buffer = line
                self.notify("Copied. Open a shell and paste it (prefix ]).", timeout=4)

        self.push_screen(ToolkitScreen(self.profile), insert)

    def set_option(self, key: str, value: str) -> None:
        """Change a setting now; Save settings keeps it for next time."""
        self.settings = config.replace(self.settings, **{key: value})
        if key == "theme":
            theme.apply(self, value)
        elif key == "prefix":
            self.prefix = value
        elif key == "profile":
            self.profile = value
        elif key == "shell":
            self.shell = next((s for s in self.shells if s.name == value), self.shell)
        self.notify(f"{key}: {value}  (Save settings to keep it)", timeout=3)
        self._refresh_status()

    def action_save_settings(self) -> None:
        try:
            self.notify(f"Saved {config.save(self.settings)}", timeout=3)
        except OSError as exc:
            self.notify(f"Could not save settings: {exc}", severity="error")

    def action_help(self) -> None:
        self.push_screen(Help(HELP.format(prefix=KEY_NAMES.get(self.prefix, self.prefix))))

    def action_quit_app(self) -> None:
        count = len(self.all_panes())
        if count <= 1:
            self.exit()
            return
        self.push_screen(Confirm(f"Quit? {count} panes and their programs will end.", ok="Quit"),
                         lambda ok: ok and self.exit())

    # prefix key (called by the focused pane before it sends a key to the shell)
    PREFIX_COMMANDS = {
        "c": ("action_new_tab",), "n": ("action_cycle_tab", 1), "p": ("action_cycle_tab", -1),
        ",": ("action_rename_tab",), "&": ("action_close_tab",),
        "%": ("action_split", "right"), "|": ("action_split", "right"),
        '"': ("action_split", "down"), "-": ("action_split", "down"),
        "left": ("action_focus", "left"), "right": ("action_focus", "right"),
        "up": ("action_focus", "up"), "down": ("action_focus", "down"),
        "h": ("action_focus", "left"), "l": ("action_focus", "right"),
        "k": ("action_focus", "up"), "j": ("action_focus", "down"),
        "o": ("action_next_pane",), "z": ("action_zoom",), "x": ("action_close_pane",),
        "[": ("action_copy_mode",), "]": ("action_paste_buffer",),
        "t": ("action_task_manager",), "g": ("action_toolkit",), ":": ("action_command_palette",), "P": ("action_command_palette",),
        "?": ("action_help",), "H": ("action_home",), "m": ("action_manual",),
        **{str(i): ("action_select_tab", i - 1) for i in range(1, 10)},
    }

    def pane_key(self, pane: TerminalPane, event) -> bool:
        if self._prefix_armed:
            self._prefix_armed = False
            self._refresh_status()
            if event.key == self.prefix:                          # prefix twice: send it through
                return False
            ch = event.character
            command = self.PREFIX_COMMANDS.get(ch) if ch and ch.isprintable() else None
            command = command or self.PREFIX_COMMANDS.get(event.key)
            if command:
                result = getattr(self, command[0])(*command[1:])
                if hasattr(result, "__await__"):
                    self.run_worker(result, exclusive=False)
            return True
        if event.key == self.prefix and pane.copy is None:
            self._prefix_armed = True
            self._refresh_status()
            return True
        return False

    # status bar and labels
    def _label(self, tab_id: str, pane: TerminalPane | None) -> str:
        ids = self._tab_ids()
        n = ids.index(tab_id) + 1 if tab_id in ids else len(ids) + 1
        name = self._named.get(tab_id) or (pane.title if pane else self.shell.name)
        return f"{n} {name}"[:32]

    def _refresh_labels(self) -> None:
        for tab_id in self._tab_ids():
            pane = self._last_pane.get(tab_id)
            if pane is None or not pane.is_attached:
                panes = self._tab_panes(tab_id)
                pane = panes[0] if panes else None
            try:
                self.tabbed.get_tab(tab_id).label = self._label(tab_id, pane)
            except Exception:  # noqa: BLE001 - tab being removed
                pass
        self._refresh_status()

    def _refresh_status(self) -> None:
        try:
            left = self.query_one("#status-left", Static)
        except Exception:  # noqa: BLE001 - not mounted yet
            return
        t = Text()
        t.append(" mindas ", style="bold #070b1a on #7aa2ff")
        if self._prefix_armed:
            t.append(f" {KEY_NAMES.get(self.prefix, self.prefix)} ", style="bold #070b1a on #fbbf24")
        pane = self.current_pane()
        if pane is not None and pane.copy is not None:
            t.append(" COPY ", style="bold #070b1a on #5eead4")
        if self._zoomed:
            t.append(" ZOOM ", style="bold #070b1a on #b18cff")
        if pane is not None:
            t.append(f"  {pane.shell.name}", style="#e6e9f5")
            panes = len(self._tab_panes(self.tabbed.active))
            if panes > 1:
                t.append(f"  {panes} panes", style="#8b93b8")
        left.update(t)

    def _update_system(self) -> None:
        try:
            import psutil

            cpu, ram = psutil.cpu_percent(), psutil.virtual_memory().percent
            self._sys = f"CPU {cpu:4.1f}%  RAM {ram:4.1f}%  {time.strftime('%H:%M')} "
        except Exception:  # noqa: BLE001 - status is best effort
            self._sys = time.strftime("%H:%M ")
        try:
            self.query_one("#status-right", Static).update(self._sys)
        except Exception:  # noqa: BLE001
            pass
        self._refresh_status()


# Short alias used by tools/e2e.py.
TerminalApp = MindasTerminal


def main(argv: list[str] | None = None) -> int:
    settings, warnings = config.load()
    p = argparse.ArgumentParser(prog="mindas-terminal",
                                description="A universal terminal for Windows and Linux: tabs, splits, copy mode, "
                                            "task manager, toolkits for every field. Bash first everywhere.",
                                epilog=f"Settings file: {config.path()}  (command-line options win)")
    p.add_argument("--shell", help="shell to use, by name (see --list-shells); default: bash first")
    p.add_argument("--list-shells", action="store_true", help="list detected shells and exit")
    p.add_argument("--prefix", help=f"prefix key for tab and pane commands (default: {settings.prefix})")
    p.add_argument("--scrollback", type=int, help=f"lines of scrollback per pane (default: {settings.scrollback})")
    p.add_argument("--cwd", help="start directory for new shells")
    p.add_argument("--profile", choices=sorted(toolkit.FIELDS), help="your field: its toolkit commands come first")
    p.add_argument("--theme", choices=config.THEMES, help=f"colours (default: {settings.theme})")
    p.add_argument("--aliases", choices=["bash", "powershell", "list"],
                   help="print opt-in aliases and helper functions for a shell, then exit")
    p.add_argument("--alias-style", choices=config.ALIAS_STYLES,
                   help="powershell aliases: linux adds Linux command names (touch, which, grep...); native does not")
    p.add_argument("--init-config", action="store_true", help="write a settings file with the defaults and exit")
    p.add_argument("--no-home", action="store_true", help="start in a shell instead of the home window")
    p.add_argument("--man", action="store_true", help="print the manual page (roff) and exit")
    p.add_argument("--version", action="version", version=f"mindas-terminal {__version__}")
    args = p.parse_args(argv)
    for w in warnings:
        print(f"mindas-terminal: {w}", file=sys.stderr)
    if args.man:
        from . import manpage

        sys.stdout.write(manpage.render())
        return 0
    if args.no_home:
        settings = config.replace(settings, show_home=False)
    if args.init_config:
        target = config.path()
        if target.exists():
            print(f"exists, not overwritten: {target}")
        else:
            print(f"written: {config.save(settings)}")
        return 0
    if args.aliases:
        style = args.alias_style or settings.alias_style
        out = {"bash": aliases.bash, "powershell": lambda: aliases.powershell(style), "list": aliases.listing}
        sys.stdout.write(out[args.aliases]())
        return 0
    found = shells.detect()
    if args.list_shells:
        for s in found:
            print(f"{s.name:<20} {' '.join(s.argv)}")
        return 0
    if not found:
        print("no shell found", file=sys.stderr)
        return 1
    wanted = args.shell or settings.shell
    shell = found[0]
    if wanted:
        shell = next((s for s in found if wanted.lower() in s.name.lower()), None)
        if shell is None:
            print(f"shell not found: {wanted}. Available: {', '.join(s.name for s in found)}", file=sys.stderr)
            return 2
    if args.theme:
        settings = config.replace(settings, theme=args.theme)
    scrollback = args.scrollback if args.scrollback is not None else settings.scrollback
    MindasTerminal(shell, prefix=args.prefix or settings.prefix, scrollback=min(max(scrollback, 0), 1_000_000), cwd=args.cwd,
                   available=found, profile=args.profile, settings=settings).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
