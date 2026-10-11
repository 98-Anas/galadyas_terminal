# Task Manager

`prefix t` opens a full-screen process view. It refreshes every two seconds and never blocks the terminals
behind it.

## What it shows

**Header:** CPU (all cores) with load average on Linux, RAM and swap, and one line per NVIDIA GPU with
utilisation and memory.

**Table:**

| Column | Meaning |
|---|---|
| PID | Process ID |
| NAME | Program name |
| USER | Owner (domain removed on Windows) |
| CPU% | Share of one core since the last refresh (more than 100 on multi-threaded work); yellow from 10, red from 50 |
| MEM% | Resident memory as a share of RAM |
| RSS | Resident memory |
| GPU MiB | GPU memory used by the process (NVIDIA) |
| COMMAND | Full command line |

GPU data comes from `nvidia-smi`, looked up only in absolute `PATH` folders and never in the current folder
(see [Security](Security)). On
Windows with WDDM drivers, per-process GPU memory may be unavailable; the totals in the header still work.

## Keys

| Keys | Action |
|---|---|
| `c` `m` `g` `p` `n` | Sort by CPU, memory, GPU, PID, name. Press again to reverse |
| `/` | Filter. Matches name, command line, user, or exact PID. `Esc` clears |
| `f` | Only processes started from this terminal: every pane's shell and everything below it |
| `k` | Terminate the selected process (polite: it can clean up) |
| `K` | Kill it (immediate, no clean-up) |
| `r` | Refresh now |
| `q`, `Esc` | Close |

## Ending processes safely

- Both `k` and `K` show the full command line and ask for confirmation. The safe choice, *Cancel*, has focus.
- System processes (PID 0, 1 and 4) and galadyas terminal itself are refused.
- Ending another user's or a system process needs administrator or root rights; you get a clear message
  instead of an error.

## Field examples

- **AI:** sort by `g` to see which training run holds the GPU memory; `f` to see only the runs you started here.
- **Data:** filter `/python` or `/spark` to find a runaway notebook kernel; sort by `m`.
- **DevOps:** filter `/docker` or `/kubectl` to see port-forwards left running.
- **Security:** sort by `p` and scan the COMMAND column for unexpected programs; compare with `prefix g` →
  *Listening services on this machine*.
- **IT support:** sort by `c` to find what makes a machine slow, then `k` it with the user's permission.
