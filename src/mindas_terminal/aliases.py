"""Opt-in aliases and helper functions for bash/zsh and PowerShell.

Nothing is installed automatically. Print them with `mindas-terminal --aliases bash` (or `powershell`),
read them, then add them to your shell yourself. Every helper is local-only: none sends data anywhere
except `myip`, which asks a public service for your address and says so.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Alias:
    name: str
    group: str
    help: str
    bash: str           # body of a bash function (or alias value when it starts with "=")
    powershell: str = ""


A = Alias
ALIASES: tuple[Alias, ...] = (
    # navigation
    A("..", "navigation", "up one folder", "=cd ..", "Set-Location .."),
    A("...", "navigation", "up two folders", "=cd ../..", "Set-Location ../.."),
    A("up", "navigation", "up N folders: up 3", 'local n="${1:-1}" p=""; for ((i=0;i<n;i++)); do p="../$p"; done; cd "${p:-.}"',
      'param([int]$n = 1); Set-Location ((1..$n | ForEach-Object { ".." }) -join "/")'),
    A("mkcd", "navigation", "make a folder and enter it", 'mkdir -p -- "$1" && cd -- "$1"',
      'param($d); New-Item -ItemType Directory -Force -Path $d | Out-Null; Set-Location $d'),
    A("cdg", "navigation", "go to the top of the git repository", 'cd "$(git rev-parse --show-toplevel)"',
      'Set-Location (git rev-parse --show-toplevel)'),
    A("bm", "navigation", "bookmark this folder as NAME: bm work",
      'mkdir -p ~/.config/mindas-terminal && echo "$1=$PWD" >> ~/.config/mindas-terminal/bookmarks && echo "saved $1"'),
    A("go", "navigation", "jump to a bookmark: go work",
      'local d; d="$(grep -m1 "^$1=" ~/.config/mindas-terminal/bookmarks 2>/dev/null | cut -d= -f2-)"; [ -n "$d" ] && cd "$d" || echo "no bookmark: $1"'),
    # listing and files
    A("ll", "files", "long list, human sizes", "=ls -lAh --color=auto", "Get-ChildItem -Force"),
    A("lt", "files", "newest files last", "=ls -lAhtr --color=auto",
      "Get-ChildItem -Force | Sort-Object LastWriteTime"),
    A("lsize", "files", "largest items here", "du -sh -- * .[!.]* 2>/dev/null | sort -hr | head -20",
      "Get-ChildItem | Sort-Object Length -Descending | Select-Object -First 20 Name, Length"),
    A("ff", "files", "find files by name: ff report", 'find . -iname "*$1*" -not -path "*/.git/*" 2>/dev/null',
      'param($n); Get-ChildItem -Recurse -Filter "*$n*" -ErrorAction SilentlyContinue'),
    A("ft", "files", "find text in files: ft TODO", 'grep -rIn --color=auto --exclude-dir={.git,node_modules,.venv} -- "$1" .',
      'param($t); Get-ChildItem -Recurse -File | Select-String -Pattern $t'),
    A("bak", "files", "timestamped backup copy: bak config.yml", 'cp -a -- "$1" "$1.$(date +%Y%m%d-%H%M%S).bak"',
      'param($f); Copy-Item $f "$f.$(Get-Date -Format yyyyMMdd-HHmmss).bak"'),
    A("extract", "files", "extract any archive: extract file.tar.gz",
      'case "$1" in *.tar.gz|*.tgz) tar -xzf "$1";; *.tar.bz2) tar -xjf "$1";; *.tar.xz) tar -xJf "$1";; *.tar) tar -xf "$1";; '
      '*.zip) unzip "$1";; *.gz) gunzip "$1";; *.7z) 7z x "$1";; *) echo "unknown archive: $1";; esac',
      'param($f); Expand-Archive $f'),
    A("cpv", "files", "copy with progress (rsync)", '=rsync -ah --info=progress2'),
    A("count", "files", "files per extension here", "find . -type f -not -path '*/.git/*' | sed -n 's/.*\\.//p' | sort | uniq -c | sort -nr | head -20"),
    # safety
    A("rmi", "safety", "remove, asking for each file", "=rm -i", "Remove-Item -Confirm"),
    A("cpi", "safety", "copy, asking before overwrite", "=cp -i"),
    A("mvi", "safety", "move, asking before overwrite", "=mv -i"),
    A("trash", "safety", "move to ~/.trash instead of deleting", 'mkdir -p ~/.trash && mv -- "$@" ~/.trash/',
      'param($f); Add-Type -AssemblyName Microsoft.VisualBasic; [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile((Resolve-Path $f), "OnlyErrorDialogs", "SendToRecycleBin")'),
    # system
    A("psg", "system", "find processes: psg python", 'ps aux | grep -i -- "$1" | grep -v grep',
      'param($n); Get-Process | Where-Object Name -like "*$n*"'),
    A("ports", "system", "listening ports", "=ss -tulpn 2>/dev/null || netstat -an | grep LISTEN",
      "Get-NetTCPConnection -State Listen | Sort-Object LocalPort"),
    A("meminfo", "system", "memory overview", "=free -h",
      "Get-CimInstance Win32_OperatingSystem | Select-Object FreePhysicalMemory, TotalVisibleMemorySize"),
    A("diskinfo", "system", "disk space", "=df -h", "Get-PSDrive -PSProvider FileSystem"),
    A("path", "system", "PATH, one entry per line", "echo \"$PATH\" | tr ':' '\\n'", '$env:Path -split ";"'),
    A("h", "system", "search history: h docker", 'history | grep -i -- "$1"',
      'param($t); Get-Content (Get-PSReadLineOption).HistorySavePath | Select-String $t'),
    A("now", "system", "date and time, ISO format", "=date '+%Y-%m-%d %H:%M:%S'", "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'"),
    A("reload", "system", "reload the shell profile", "source ~/.bashrc", ". $PROFILE"),
    # network
    A("myip", "network", "public IP (asks ifconfig.me)", "=curl -s https://ifconfig.me; echo", "(Invoke-RestMethod https://ifconfig.me)"),
    A("localip", "network", "local IP addresses", "hostname -I 2>/dev/null || ipconfig",
      "Get-NetIPAddress -AddressFamily IPv4 | Select-Object InterfaceAlias, IPAddress"),
    A("serve", "network", "share this folder on localhost:8000 only",
      'python3 -m http.server "${1:-8000}" --bind 127.0.0.1',
      'param($p = 8000); python -m http.server $p --bind 127.0.0.1'),
    A("headers", "network", "HTTP response headers: headers https://example.com", 'curl -sSI -- "$1"',
      'param($u); (Invoke-WebRequest $u -Method Head).Headers'),
    A("certexp", "network", "TLS certificate expiry: certexp example.com",
      'echo | openssl s_client -connect "$1:443" -servername "$1" 2>/dev/null | openssl x509 -noout -dates'),
    # git
    A("gs", "git", "short status", "=git status -sb", "git status -sb"),
    A("gl", "git", "history graph", "=git log --oneline --graph --decorate -20", "git log --oneline --graph --decorate -20"),
    A("gd", "git", "unstaged diff", "=git diff", "git diff"),
    A("gds", "git", "staged diff", "=git diff --staged", "git diff --staged"),
    A("gco", "git", "switch branch", "=git switch", "git switch $args"),
    A("gcb", "git", "new branch", "=git switch -c", "git switch -c $args"),
    A("gundo", "git", "undo last commit, keep changes", "=git reset --soft HEAD~1", "git reset --soft HEAD~1"),
    A("gwip", "git", "quick work-in-progress commit", "git add -A && git commit -m 'wip' --no-verify",
      "git add -A; git commit -m 'wip' --no-verify"),
    A("gclean", "git", "delete merged branches", "git branch --merged | grep -vE '^\\*|main|master|dev' | xargs -r git branch -d"),
    # containers
    A("dps", "devops", "running containers", "docker ps --format 'table {{.Names}}\\t{{.Image}}\\t{{.Status}}\\t{{.Ports}}'",
      "docker ps --format 'table {{.Names}}\\t{{.Image}}\\t{{.Status}}\\t{{.Ports}}'"),
    A("dlog", "devops", "follow container logs: dlog web", 'docker logs -f --tail 100 "$1"', "docker logs -f --tail 100 $args"),
    A("dsh", "devops", "shell in a container: dsh web", 'docker exec -it "$1" sh -c "bash || sh"',
      'docker exec -it $args sh -c "bash || sh"'),
    A("dclean", "devops", "remove stopped containers and dangling images", "docker container prune -f && docker image prune -f"),
    A("k", "devops", "kubectl", "=kubectl", "kubectl $args"),
    A("kgp", "devops", "pods in the current namespace", "=kubectl get pods -o wide", "kubectl get pods -o wide"),
    A("kbad", "devops", "pods that are not running", "kubectl get pods -A --field-selector=status.phase!=Running"),
    A("kns", "devops", "switch namespace: kns prod", 'kubectl config set-context --current --namespace="$1"'),
    A("tfp", "devops", "terraform plan to a file", "terraform plan -out=tfplan"),
    # hpc
    A("sq", "hpc", "my Slurm jobs", 'squeue -u "$USER" -o "%.10i %.20j %.8T %.10M %.6D %R"'),
    A("sgpu", "hpc", "interactive GPU shell (1 GPU, 2 hours)", "srun --gres=gpu:1 --cpus-per-task=8 --mem=32G --time=02:00:00 --pty bash"),
    A("sacct1", "hpc", "today's finished jobs", 'sacct -u "$USER" --starttime today --format=JobID,JobName%20,State,Elapsed,MaxRSS'),
    A("sfree", "hpc", "partitions and idle nodes", "sinfo -o '%P %a %l %D %t' | grep -E 'idle|mix|PARTITION'"),
    # ai and data
    A("gpu", "ai", "GPU use", "=nvidia-smi", "nvidia-smi"),
    A("gpuw", "ai", "GPU use, refresh every second", "=nvidia-smi -l 1", "nvidia-smi -l 1"),
    A("torchok", "ai", "is PyTorch using the GPU",
      "python -c 'import torch; print(torch.__version__, \"cuda\" if torch.cuda.is_available() else \"cpu only\")'"),
    A("venv", "ai", "create or activate .venv here",
      '[ -d .venv ] || python3 -m venv .venv; . .venv/bin/activate 2>/dev/null || . .venv/Scripts/activate',
      'if (-not (Test-Path .venv)) { python -m venv .venv }; .\\.venv\\Scripts\\Activate.ps1'),
    A("json", "data", "pretty-print JSON from a file or stdin", 'python3 -m json.tool "${1:-/dev/stdin}"',
      'param($f); Get-Content $f -Raw | ConvertFrom-Json | ConvertTo-Json -Depth 20'),
    A("csvhead", "data", "first rows of a CSV as a table", 'head -"${2:-20}" "$1" | column -s, -t'),
    A("sql", "data", "SQL over CSV/Parquet with DuckDB: sql \"select * from 'x.csv'\"", 'duckdb -c "$1"'),
    # security
    A("sha", "security", "SHA-256 of a file", 'sha256sum -- "$1"', 'param($f); Get-FileHash $f -Algorithm SHA256'),
    A("genpass", "security", "strong random password", "openssl rand -base64 24",
      "$b = New-Object byte[] 18; [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($b); "
      "[Convert]::ToBase64String($b)"),           # cryptographic randomness, like openssl rand
    A("listening", "security", "services listening on this machine", "=ss -tulpn",
      "Get-NetTCPConnection -State Listen | Sort-Object LocalPort"),
    A("lastfail", "security", "recent failed logins", "journalctl -u ssh --since today 2>/dev/null | grep -i failed || lastb | head",
      "Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4625} -MaxEvents 20"),
)

# Linux command names for PowerShell (alias_style = "linux"). In bash these are the real commands.
L = "linux"
LINUX_STYLE: tuple[Alias, ...] = (
    A("touch", L, "create a file or update its time", "", 'param($f); if (Test-Path $f) { (Get-Item $f).LastWriteTime = Get-Date } else { New-Item -ItemType File $f | Out-Null }'),
    A("which", L, "where a command comes from", "", 'param($c); (Get-Command $c -ErrorAction SilentlyContinue).Source'),
    A("grep", L, "search text: grep pattern file", "", 'param($p, $f); if ($f) { Select-String -Pattern $p -Path $f } else { $input | Select-String -Pattern $p }'),
    A("head", L, "first lines: head file 20", "", 'param($f, $n = 10); Get-Content $f -TotalCount $n'),
    A("tail", L, "last lines: tail file 20", "", 'param($f, $n = 10); Get-Content $f -Tail $n'),
    A("tailf", L, "follow a file", "", 'param($f); Get-Content $f -Tail 20 -Wait'),
    A("wc", L, "count lines, words, characters", "", 'param($f); Get-Content $f | Measure-Object -Line -Word -Character'),
    A("df", L, "disk space", "", 'Get-PSDrive -PSProvider FileSystem | Select-Object Name, @{n="UsedGB";e={[math]::Round($_.Used/1GB,1)}}, @{n="FreeGB";e={[math]::Round($_.Free/1GB,1)}}'),
    A("du", L, "folder size: du path", "", 'param($d = "."); "{0:N1} MB" -f ((Get-ChildItem $d -Recurse -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum / 1MB)'),
    A("free", L, "memory", "", '$o = Get-CimInstance Win32_OperatingSystem; "total {0:N1} GB  free {1:N1} GB" -f ($o.TotalVisibleMemorySize/1MB), ($o.FreePhysicalMemory/1MB)'),
    A("uptime", L, "time since boot", "", '(Get-Date) - (Get-CimInstance Win32_OperatingSystem).LastBootUpTime'),
    A("uname", L, "system name and version", "", '"Windows $([Environment]::OSVersion.Version) $env:PROCESSOR_ARCHITECTURE"'),
    A("nproc", L, "number of CPUs", "", '[Environment]::ProcessorCount'),
    A("top", L, "top processes by CPU", "", 'Get-Process | Sort-Object CPU -Descending | Select-Object -First 15 Id, ProcessName, CPU, WS'),
    A("pkill", L, "stop processes by name (asks first)", "", 'param($n); Get-Process -Name $n | Stop-Process -Confirm'),
    A("ifconfig", L, "network addresses", "", 'ipconfig'),
    A("env", L, "environment variables", "", 'Get-ChildItem Env: | Sort-Object Name'),
    A("export", L, "set a variable: export NAME=value", "", 'param($kv); $k, $v = $kv -split "=", 2; Set-Item "Env:$k" $v'),
    A("man", L, "help for a command", "", 'param($c); Get-Help $c -Full'),
    A("ln", L, "symbolic link: ln -s target link", "", 'param($s, $t, $l); New-Item -ItemType SymbolicLink -Path $l -Target $t'),
    A("unzip", L, "extract a zip", "", 'param($f); Expand-Archive $f'),
    A("open", L, "open with the default app (xdg-open)", "", 'param($f = "."); Invoke-Item $f'),
    A("sudo", L, "run as administrator (new window, asks)", "", 'Start-Process powershell -Verb RunAs -ArgumentList ("-NoExit -Command " + ($args -join " "))'),
)

GROUPS = ("linux", "navigation", "files", "safety", "system", "network", "git", "devops", "hpc", "ai", "data", "security")


def bash() -> str:
    out = ["# mindas-terminal aliases for bash and zsh. Review before use.",
           "# Add to ~/.bashrc:  eval \"$(mindas-terminal --aliases bash)\"", ""]
    for g in GROUPS:
        out.append(f"# {g}")
        for a in (a for a in ALIASES if a.group == g and a.bash):
            if a.bash.startswith("="):
                out.append(f"alias {a.name}='{a.bash[1:]}'" if "'" not in a.bash else f'alias {a.name}="{a.bash[1:]}"')
            elif a.name.isidentifier() or a.name.replace("_", "").isalnum():
                out.append(f"{a.name}() {{ {a.bash}; }}")
        out.append("")
    out.append("malias() { mindas-terminal --aliases list; }")
    return "\n".join(out) + "\n"


def powershell(style: str = "linux") -> str:
    out = ["# mindas-terminal functions for PowerShell. Review before use.",
           "# Add to $PROFILE:  mindas-terminal --aliases powershell | Out-String | Invoke-Expression", ""]
    for g in GROUPS:
        pool = ALIASES + (LINUX_STYLE if style == "linux" else ())
        items = [a for a in pool if a.group == g and a.powershell]
        if not items:
            continue
        out.append(f"# {g}")
        for a in items:
            name = {"..": "cd..", "...": "cd..."}.get(a.name, a.name)
            if name in BUILTIN_PS_ALIASES:                         # replace PowerShell's own alias of that name
                out.append(f"Remove-Item -Force -ErrorAction SilentlyContinue Alias:{name}")
            out.append(f"function {name} {{ {a.powershell} }}")
        out.append("")
    return "\n".join(out) + "\n"


BUILTIN_PS_ALIASES = {"h", "gl", "gd", "gs", "gp", "gcb", "ls", "cd", "rm", "man", "sl", "kill", "ps", "curl",
                      "wget", "diff", "sort", "tee", "where", "echo", "cat", "cp", "mv", "pwd", "clear", "history"}


def listing() -> str:
    out = []
    for g in GROUPS:
        out.append(f"{g}:" + ("  (PowerShell only; bash has the real commands)" if g == "linux" else ""))
        out.extend(f"  {a.name:<10} {a.help}" for a in ALIASES + LINUX_STYLE if a.group == g)
    return "\n".join(out) + "\n"
