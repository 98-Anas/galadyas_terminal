# Field Guides

A starting set-up for each role. Every guide uses only what ships with the app: a profile for the toolkits,
a pane layout, aliases and the task manager. Mix freely; many people work across several fields.

## DevOps and cloud engineers

```bash
galadyas-terminal --profile devops
eval "$(galadyas-terminal --aliases bash)"
```

- **Layout:** left pane for work, `prefix "` below it for `kubectl get pods -w` or `docker compose logs -f`.
- **Toolkit:** `prefix g` then `pods not running`, `describe`, `terraform plan`, `compose`.
- **Aliases:** `dps`, `dlog web`, `dsh web`, `kbad`, `kns staging`, `tfp`.
- **Task manager:** filter `/kubectl` to find forgotten `port-forward` processes.
- **Habit:** use *Terraform: review a plan*, then *apply the reviewed plan*: the plan file makes the apply exact.

## HPC users and administrators

```bash
galadyas-terminal --profile hpc
```

- **Layout:** one tab per cluster (`prefix c`, `ssh login.cluster`), `prefix ,` to name it.
- **Toolkit:** `pending`, `sacct`, `interactive gpu`, `partitions`, `rsync results`.
- **Aliases:** `sq` (your queue, readable), `sgpu` (interactive GPU shell), `sacct1`, `sfree`.
- **Copy mode:** `prefix [` and `/error` in long job logs; `V` `y` to copy a failing line into a ticket.
- **Remote persistence:** run a session manager on the login node for jobs you must reattach to; use `--prefix ctrl+a`
  here so both prefixes work.

## AI and ML engineers

```bash
galadyas-terminal --profile ai
```

- **Layout:** training on the left, `prefix %` and `nvidia-smi -l 1` (alias `gpuw`) on the right, `prefix "`
  for `tensorboard --logdir runs`.
- **Task manager:** `g` sorts by GPU memory, so you see which run holds it; `f` shows only runs from this window.
- **Toolkit:** `is pytorch using the gpu`, `hugging face`, `tensorboard`, `survives logout`.
- **Aliases:** `torchok`, `venv`, `gpu`.

## Data engineers

```bash
galadyas-terminal --profile data-eng
```

- **Toolkit:** `parquet schema`, `csv to parquet`, `table sizes`, `json lines`.
- **Aliases:** `sql "select count(*) from 'events.parquet'"`, `json file.json`, `csvhead file.csv`.
- **Copy mode:** search query plans and error output; copy a failing record with `V` `y`.

## Data scientists

```bash
galadyas-terminal --profile data-sci
```

- **Layout:** `prefix c` for a JupyterLab tab (*Start JupyterLab* in the toolkit), another for git.
- **Toolkit:** `quick look`, `missing values`, `render a notebook`, `freeze`.
- **Task manager:** filter `/python` to find a notebook kernel that holds too much memory; sort by `m`.

## Cybersecurity (defenders and authorised testers)

```bash
galadyas-terminal --profile security
```

- **Toolkit:** `listening services`, `tls certificate`, `file hash`, `verify a signature`, `failed logins`,
  `suid`, `secrets committed`, `vulnerabilities`.
- **Aliases:** `listening`, `sha file`, `certexp host`, `lastfail`, `genpass`.
- **Task manager:** sort by PID and review command lines for unknown programs.
- **Copy mode:** search logs for an IP or user; copy evidence lines exactly as printed.
- **Scope:** scan only systems you own or have written authorisation to test, and keep that authorisation
  with your notes. See [Security](Security).

## IT support and system administrators

```bash
galadyas-terminal --profile linux        # or --profile windows on Windows
```

- **Windows:** `prefix g` then `stopped services`, `system errors`, `system files`, `repair`, `who is using a port`.
  With `alias_style = "linux"`, `df`, `free`, `uptime`, `top` and `which` work in PowerShell too.
- **Linux:** `disk usage`, `service status`, `recent system errors`, `largest files`.
- **Task manager:** sort by CPU to find what makes a computer slow; end it with the user's permission.
- **Remote help:** open a tab per machine (`ssh`), name tabs after the ticket number with `prefix ,`.

## Networking

```bash
galadyas-terminal --profile network
```

- **Toolkit:** `reachable`, `path to a host`, `dns`, `tcp port open`, `http headers`.
- **Aliases:** `localip`, `myip` (contacts ifconfig.me), `headers url`, `ports`.

## IT project managers and team leads

```bash
galadyas-terminal --profile pm
```

- **Toolkit:** `commits this week`, `release notes`, `open pull requests`, `issues assigned to me`,
  `lines changed`, `activity per day`, `work in progress notes`.
- **Workflow:** one tab per repository; before a status meeting, run *Commits this week by author* and
  *Release notes since the last tag* and copy the output with copy mode (`V`, `G`, `y`).
- The `gh` commands need the [GitHub CLI](https://cli.github.com/) and a login (`gh auth login`).

## Students and learners

- Open the toolkits and read the commands for a field you are learning: each one says what it does.
- Use the [Keyboard Reference](Keyboard-Reference) as practice for keyboard habits that transfer to
  servers everywhere.
