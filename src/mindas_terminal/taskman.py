"""Task manager screen: processes with CPU, memory and GPU use; sort, filter, end with confirmation."""

from __future__ import annotations

import time
from dataclasses import replace

from rich.text import Text
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Input, Static

from . import tasks
from .dialogs import Confirm

COLUMNS = (("PID", 8), ("NAME", 26), ("USER", 12), ("CPU%", 7), ("MEM%", 6), ("RSS", 8), ("GPU MiB", 8), ("COMMAND", None))


def _bar(pct: float, width: int = 12) -> str:
    filled = int(round(min(max(pct, 0), 100) / 100 * width))
    return "█" * filled + "░" * (width - filled)


class TaskManager(Screen[None]):
    DEFAULT_CSS = """
    TaskManager { background: $background; }
    #tm-head { height: auto; padding: 0 1; background: $panel; color: $text; }
    #tm-filter { display: none; height: 3; }
    #tm-filter.shown { display: block; }
    #tm-table { height: 1fr; }
    """
    BINDINGS = [
        Binding("q,escape", "close", "Close"),
        Binding("slash", "filter", "Filter"),
        Binding("c", "sort('cpu')", "CPU"), Binding("m", "sort('mem')", "Memory"),
        Binding("g", "sort('gpu')", "GPU"), Binding("p", "sort('pid')", "PID"), Binding("n", "sort('name')", "Name"),
        Binding("f", "only_terminal", "This terminal"),
        Binding("k", "end(False)", "Terminate"), Binding("K", "end(True)", "Kill"),
        Binding("r", "refresh_now", "Refresh"),
    ]

    def __init__(self, pane_pids=lambda: set(), interval: float = 2.0) -> None:
        super().__init__()
        self._pane_pids = pane_pids
        self._interval = interval
        self.sort, self.reverse, self.filter_text, self.only_terminal = "cpu", True, "", False
        self._procs: list[tasks.Proc] = []

    def compose(self) -> ComposeResult:
        yield Static("collecting...", id="tm-head")
        yield Input(placeholder="filter by name, command, user or pid (Enter to apply, Esc to clear)", id="tm-filter")
        table = DataTable(id="tm-table", cursor_type="row", zebra_stripes=True)
        for label, width in COLUMNS:
            table.add_column(label, width=width)
        yield table
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(DataTable).focus()
        self._measured = False
        self._busy = False
        self.refresh_data()

    def refresh_data(self) -> None:
        """Start a collection unless one is running; the next one is scheduled when this one finishes,
        so a slow machine is never asked to collect twice at once."""
        if not self._busy:
            self._busy = True
            self._collect()

    @work(thread=True, group="tasks")
    def _collect(self) -> None:
        try:
            if not self._measured:
                # CPU use is a difference between two samples: show the list at once, then measured values.
                first = tasks.collect()
                self.app.call_from_thread(self._show, first, tasks.system(with_gpu=False), True)
                time.sleep(0.8)
            gpu = tasks.gpu_processes()
            procs = tasks.collect(gpu)
            sysinfo = tasks.system()
            self._measured = True
            self.app.call_from_thread(self._show, procs, sysinfo)
        finally:
            self.app.call_from_thread(self._done)

    def _done(self) -> None:
        self._busy = False
        if self.is_attached:
            self.set_timer(self._interval, self.refresh_data)

    def _show(self, procs: list[tasks.Proc], s: tasks.System, measuring: bool = False) -> None:
        self._procs = procs
        if not measuring:
            s = replace(s, cpu=tasks.total_cpu(procs, s.cores))
        ram = s.ram_used / s.ram_total * 100 if s.ram_total else 0
        lines = [
            f"CPU  {_bar(s.cpu)} {s.cpu:5.1f}%  ({s.cores} cores)"
            + (f"   load {s.load[0]:.2f} {s.load[1]:.2f} {s.load[2]:.2f}" if s.load else ""),
            f"RAM  {_bar(ram)} {ram:5.1f}%  {tasks.human(s.ram_used)} / {tasks.human(s.ram_total)}"
            + (f"   swap {tasks.human(s.swap_used)} / {tasks.human(s.swap_total)}" if s.swap_total else ""),
        ]
        for name, util, used, total in s.gpus:
            lines.append(f"GPU  {_bar(util)} {util:5.1f}%  {used} / {total} MiB  {name}")
        mode = "this terminal only" if self.only_terminal else "all processes"
        if measuring:
            lines.append("measuring CPU and GPU use...")
        lines.append(f"{len(procs)} processes   sort: {self.sort} {'desc' if self.reverse else 'asc'}   "
                     f"showing: {mode}" + (f"   filter: {self.filter_text}" if self.filter_text else ""))
        self.query_one("#tm-head", Static).update("\n".join(lines))
        self._fill()

    def _fill(self) -> None:
        table = self.query_one(DataTable)
        keep = self._selected_pid()
        only = tasks.descendants(self._procs, self._pane_pids()) if self.only_terminal else None
        rows = tasks.arrange(self._procs, self.sort, self.reverse, self.filter_text, only)
        table.clear()
        for p in rows:
            cpu = Text(f"{p.cpu:6.1f}", style="bold #f87171" if p.cpu >= 50 else ("#fbbf24" if p.cpu >= 10 else ""))
            table.add_row(str(p.pid), p.name[:28], p.user[:14], cpu, f"{p.mem:4.1f}", tasks.human(p.rss),
                          str(p.gpu_mib or ""), p.cmd[:120], key=str(p.pid))
        if keep is not None:
            try:
                table.move_cursor(row=table.get_row_index(str(keep)))
            except Exception:  # noqa: BLE001 - the process ended; keep the cursor where it is
                pass

    def _selected_pid(self) -> int | None:
        table = self.query_one(DataTable)
        if not table.row_count:
            return None
        try:
            key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key.value
            return int(key) if key else None
        except Exception:  # noqa: BLE001
            return None

    # actions
    def action_close(self) -> None:
        f = self.query_one("#tm-filter", Input)
        if f.has_focus:
            f.value, self.filter_text = "", ""
            f.remove_class("shown")
            self.query_one(DataTable).focus()
            self._fill()
            return
        self.app.pop_screen()

    def action_filter(self) -> None:
        f = self.query_one("#tm-filter", Input)
        f.add_class("shown")
        f.focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        self.filter_text = event.value
        self._fill()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.query_one(DataTable).focus()

    def action_sort(self, key: str) -> None:
        self.reverse = not self.reverse if self.sort == key else key not in ("pid", "name")
        self.sort = key
        self._fill()

    def action_only_terminal(self) -> None:
        self.only_terminal = not self.only_terminal
        self._fill()

    def action_refresh_now(self) -> None:
        self.refresh_data()

    def action_end(self, force: bool) -> None:
        pid = self._selected_pid()
        if pid is None:
            return
        proc = next((p for p in self._procs if p.pid == pid), None)
        if reason := tasks.protected(pid):
            self.notify(f"Refused: {reason}", severity="warning")
            return
        name = proc.name if proc else str(pid)
        verb = "Kill" if force else "Terminate"
        body = (proc.cmd[:400] if proc else "") + ("\n\nKill ends it immediately, without cleanup." if force else "")

        def done(ok: bool) -> None:
            if ok:
                self.notify(tasks.end(pid, force))
                self.refresh_data()

        self.app.push_screen(Confirm(f"{verb} {name} (pid {pid})?", body, verb), done)
