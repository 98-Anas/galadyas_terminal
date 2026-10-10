"""Task manager data: processes, system totals and NVIDIA GPU use. Collection is separate from the pure
sorting and filtering so the logic is testable without real processes.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass

import psutil

from .shells import safe_which


@dataclass(frozen=True)
class Proc:
    pid: int
    ppid: int
    name: str
    user: str
    cpu: float          # percent of one core
    mem: float          # percent of RAM
    rss: int            # bytes
    threads: int
    status: str
    cmd: str
    gpu_mib: int = 0


@dataclass(frozen=True)
class System:
    cpu: float
    cores: int
    ram_used: int
    ram_total: int
    swap_used: int
    swap_total: int
    load: tuple[float, float, float] | None
    gpus: tuple[tuple[str, int, int, int], ...]     # name, util %, used MiB, total MiB


SORT_KEYS = {
    "cpu": lambda p: p.cpu, "mem": lambda p: p.rss, "pid": lambda p: p.pid,
    "name": lambda p: p.name.lower(), "gpu": lambda p: p.gpu_mib,
}


def human(n: float) -> str:
    for unit in ("B", "K", "M", "G", "T"):
        if abs(n) < 1024 or unit == "T":
            return f"{n:.0f}{unit}" if unit in ("B", "K") else f"{n:.1f}{unit}"
        n /= 1024
    return str(n)


def arrange(procs: list[Proc], sort: str = "cpu", reverse: bool = True, query: str = "",
            only: set[int] | None = None) -> list[Proc]:
    """Filter by a case-insensitive query on name, command, user or pid, optionally limit to a pid set, sort."""
    q = query.lower().strip()
    rows = [p for p in procs
            if (only is None or p.pid in only)
            and (not q or q in p.name.lower() or q in p.cmd.lower() or q in p.user.lower() or q == str(p.pid))]
    key = SORT_KEYS.get(sort, SORT_KEYS["cpu"])
    return sorted(rows, key=key, reverse=reverse)


def total_cpu(procs: list[Proc], cores: int) -> float:
    """Machine CPU use from the same samples as the table, so header and rows always agree."""
    return min(sum(p.cpu for p in procs) / max(cores, 1), 100.0)


def descendants(procs: list[Proc], roots: set[int]) -> set[int]:
    """The roots and every process below them (what is running inside each terminal pane)."""
    children: dict[int, list[int]] = {}
    for p in procs:
        children.setdefault(p.ppid, []).append(p.pid)
    seen, stack = set(), list(roots)
    while stack:
        pid = stack.pop()
        if pid in seen:
            continue
        seen.add(pid)
        stack.extend(children.get(pid, ()))
    return seen


def protected(pid: int) -> str | None:
    """Reason a process must not be ended from here, or None."""
    if pid in (0, 1, 4):
        return "system process"
    if pid == os.getpid():
        return "this terminal itself"
    return None


# collection (side effects)
# Measured on Windows: num_threads, status and memory_percent each add about a second per refresh.
_FIELDS = ["pid", "ppid", "name", "username", "cpu_percent", "memory_info", "cmdline"]


def collect(gpu: dict[int, int] | None = None) -> list[Proc]:
    gpu = gpu or {}
    total = psutil.virtual_memory().total or 1
    out = []
    for p in psutil.process_iter(_FIELDS):          # psutil caches Process objects, so cpu_percent is a delta
        i = p.info
        if i.get("pid") == 0:                        # the idle pseudo-process: idle time, not a program
            continue
        try:
            cmd = " ".join(i.get("cmdline") or []) or (i.get("name") or "")
            mi = i.get("memory_info")
            out.append(Proc(
                pid=i["pid"], ppid=i.get("ppid") or 0, name=i.get("name") or "?",
                user=(i.get("username") or "").split("\\")[-1], cpu=i.get("cpu_percent") or 0.0,
                mem=(mi.rss / total * 100) if mi else 0.0, rss=mi.rss if mi else 0, threads=0,
                status="", cmd=cmd, gpu_mib=gpu.get(i["pid"], 0)))
        except (psutil.Error, KeyError, TypeError):
            continue
    return out


def _nvidia(args: list[str]) -> list[list[str]]:
    exe = safe_which("nvidia-smi")
    if not exe:
        return []
    try:
        r = subprocess.run([exe, *args, "--format=csv,noheader,nounits"], capture_output=True, text=True,
                           timeout=3, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except (OSError, subprocess.SubprocessError):
        return []
    return [[c.strip() for c in line.split(",")] for line in r.stdout.splitlines() if line.strip()]


def gpu_processes() -> dict[int, int]:
    out: dict[int, int] = {}
    for row in _nvidia(["--query-compute-apps=pid,used_memory"]):
        if len(row) == 2 and row[0].isdigit() and row[1].isdigit():
            out[int(row[0])] = out.get(int(row[0]), 0) + int(row[1])
    return out


def gpus() -> tuple[tuple[str, int, int, int], ...]:
    rows = []
    for row in _nvidia(["--query-gpu=name,utilization.gpu,memory.used,memory.total"]):
        if len(row) == 4 and all(c.isdigit() for c in row[1:]):
            rows.append((row[0], int(row[1]), int(row[2]), int(row[3])))
    return tuple(rows)


def system(with_gpu: bool = True) -> System:
    vm, sw = psutil.virtual_memory(), psutil.swap_memory()
    try:
        load = os.getloadavg()
    except (AttributeError, OSError):
        load = None
    return System(cpu=psutil.cpu_percent(), cores=psutil.cpu_count() or 1, ram_used=vm.used, ram_total=vm.total,
                  swap_used=sw.used, swap_total=sw.total, load=load, gpus=gpus() if with_gpu else ())


def end(pid: int, force: bool = False) -> str:
    """Terminate (or kill) a process. Returns a message for the user."""
    if reason := protected(pid):
        return f"refused: {reason}"
    try:
        p = psutil.Process(pid)
        name = p.name()
        p.kill() if force else p.terminate()
        return f"{'killed' if force else 'terminated'} {name} ({pid})"
    except psutil.NoSuchProcess:
        return f"process {pid} already ended"
    except psutil.AccessDenied:
        return f"access denied for {pid} (needs administrator or root)"
