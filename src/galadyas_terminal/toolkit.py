"""Toolkits: curated commands for each field, searchable offline.

A command is inserted at the prompt and never run automatically, so you always review it first.
Placeholders look like <host> and must be replaced before pressing Enter.

The security toolkit is for defence and for testing systems you own or are authorised in writing to test.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Tool:
    field: str
    title: str
    command: str
    note: str = ""
    platform: str = "any"            # any, linux, windows


FIELDS = {
    "linux": "Linux and IT support",
    "windows": "Windows administration",
    "network": "Networking",
    "git": "Git and code review",
    "devops": "DevOps and cloud",
    "hpc": "HPC and Slurm",
    "ai": "AI and ML engineering",
    "data-eng": "Data engineering",
    "data-sci": "Data science",
    "security": "Cybersecurity (ethical)",
    "pm": "IT project management",
}

SECURITY_NOTICE = ("Use these only on systems you own or are authorised in writing to test. "
                   "Unauthorised scanning or access is illegal in most countries.")

T = Tool
TOOLS: tuple[Tool, ...] = (
    # Linux and IT support
    T("linux", "Disk usage by folder, largest first", "du -h --max-depth=1 . | sort -hr | head -20"),
    T("linux", "Free disk space per filesystem", "df -h"),
    T("linux", "Largest files under a folder", "find <dir> -type f -printf '%s %p\\n' | sort -nr | head -20"),
    T("linux", "Follow a log file", "tail -f <file>"),
    T("linux", "Recent system errors", "journalctl -p err -b --no-pager | tail -50", platform="linux"),
    T("linux", "Service status and recent logs", "systemctl status <service> --no-pager -l", platform="linux"),
    T("linux", "Who is using a port", "ss -ltnp | grep :<port>", platform="linux"),
    T("linux", "Memory overview", "free -h", platform="linux"),
    T("linux", "Find text in files", "grep -rn --color '<text>' <dir>"),
    T("linux", "Archive a folder (tar.gz)", "tar -czvf <name>.tar.gz <dir>", "c create, z gzip, v list files, f file name"),
    T("linux", "Extract a tar.gz", "tar -xzvf <name>.tar.gz -C <dir>"),
    T("linux", "Copy a folder with progress, resumable", "rsync -avh --progress <src>/ <dest>/",
      "a keeps permissions and times; the trailing / copies the contents"),
    T("linux", "Change owner recursively", "sudo chown -R <user>:<group> <dir>", platform="linux"),
    # Windows
    T("windows", "System summary", "Get-ComputerInfo | Select-Object OsName, OsVersion, CsTotalPhysicalMemory",
      platform="windows"),
    T("windows", "Top processes by memory", "Get-Process | Sort-Object WS -Descending | Select-Object -First 15",
      platform="windows"),
    T("windows", "Services that are stopped but set to automatic",
      "Get-Service | Where-Object {$_.StartType -eq 'Automatic' -and $_.Status -ne 'Running'}", platform="windows"),
    T("windows", "Recent system errors", "Get-WinEvent -LogName System -MaxEvents 50 | Where-Object LevelDisplayName -eq 'Error'",
      platform="windows"),
    T("windows", "Network configuration", "ipconfig /all", platform="windows"),
    T("windows", "Flush DNS cache", "ipconfig /flushdns", platform="windows"),
    T("windows", "Check system files (administrator)", "sfc /scannow", platform="windows"),
    T("windows", "Repair the Windows image (administrator)", "DISM /Online /Cleanup-Image /RestoreHealth", platform="windows"),
    T("windows", "Installed updates", "Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 10",
      platform="windows"),
    T("windows", "Who is using a port", "Get-NetTCPConnection -LocalPort <port> | Select-Object OwningProcess, State",
      platform="windows"),
    # Networking
    T("network", "Is a host reachable", "ping -c 4 <host>", platform="linux"),
    T("network", "Is a host reachable", "ping -n 4 <host>", platform="windows"),
    T("network", "Path to a host", "traceroute <host>", platform="linux"),
    T("network", "Path to a host", "tracert <host>", platform="windows"),
    T("network", "DNS lookup", "nslookup <domain>"),
    T("network", "Is a TCP port open", "nc -zv <host> <port>", platform="linux"),
    T("network", "Is a TCP port open", "Test-NetConnection <host> -Port <port>", platform="windows"),
    T("network", "HTTP response headers", "curl -sSI <url>"),
    T("network", "Download a file", "curl -fLO <url>"),
    T("network", "Listening ports", "ss -tulpn", platform="linux"),
    T("network", "Public IP address", "curl -s https://ifconfig.me"),
    # Git
    T("git", "Compact history graph", "git log --oneline --graph --decorate -20"),
    T("git", "What changed, staged and unstaged", "git status -sb && git diff --stat"),
    T("git", "Undo the last commit, keep the changes", "git reset --soft HEAD~1"),
    T("git", "Find the commit that broke something", "git bisect start && git bisect bad && git bisect good <commit>"),
    T("git", "Who changed each line", "git blame -w <file>"),
    T("git", "Search history for a string", "git log -S '<text>' --oneline"),
    T("git", "Stash work including new files", "git stash push -u -m '<message>'"),
    T("git", "Delete merged local branches", "git branch --merged | grep -vE '^\\*|main|master' | xargs -r git branch -d"),
    # DevOps and cloud
    T("devops", "Running containers", "docker ps --format 'table {{.Names}}\\t{{.Image}}\\t{{.Status}}\\t{{.Ports}}'"),
    T("devops", "Run a container with a port and a folder",
      "docker run --rm -it -p <host_port>:<container_port> -v \"$PWD\":/work -w /work <image>",
      "--rm removes it on exit; -v mounts the current folder"),
    T("devops", "Container logs, follow", "docker logs -f --tail 100 <container>"),
    T("devops", "Shell inside a container", "docker exec -it <container> sh"),
    T("devops", "Disk used by Docker", "docker system df"),
    T("devops", "Compose: start in background", "docker compose up -d"),
    T("devops", "Kubernetes: pods that are not running",
      "kubectl get pods -A --field-selector=status.phase!=Running"),
    T("devops", "Kubernetes: logs of a pod", "kubectl logs -f <pod> -n <namespace>"),
    T("devops", "Kubernetes: describe a failing pod", "kubectl describe pod <pod> -n <namespace>"),
    T("devops", "Kubernetes: switch namespace", "kubectl config set-context --current --namespace=<namespace>"),
    T("devops", "Terraform: review a plan", "terraform init && terraform plan -out=tfplan"),
    T("devops", "Terraform: apply the reviewed plan", "terraform apply tfplan"),
    T("devops", "Ansible: check mode (dry run)", "ansible-playbook -i <inventory> <playbook>.yml --check --diff"),
    # HPC
    T("hpc", "My jobs in the queue", "squeue -u $USER"),
    T("hpc", "Submit a batch job", "sbatch <job>.sbatch"),
    T("hpc", "Interactive GPU session", "srun --gres=gpu:1 --cpus-per-task=8 --mem=32G --time=02:00:00 --pty bash"),
    T("hpc", "Cancel a job", "scancel <jobid>"),
    T("hpc", "Accounting for finished jobs", "sacct -u $USER --starttime today --format=JobID,JobName,State,Elapsed,MaxRSS"),
    T("hpc", "Partitions and free nodes", "sinfo -o '%P %a %l %D %t'"),
    T("hpc", "Why a job is pending", "squeue -j <jobid> -o '%i %T %r'"),
    T("hpc", "Available software modules", "module avail"),
    T("hpc", "Copy results back from a cluster", "rsync -avh --progress <user>@<cluster>:<path> ./"),
    # AI and ML
    T("ai", "GPU use, refresh every second", "nvidia-smi -l 1"),
    T("ai", "GPU processes", "nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv"),
    T("ai", "Is PyTorch using the GPU",
      "python -c \"import torch; print(torch.__version__, torch.cuda.is_available())\""),
    T("ai", "New project environment with uv", "uv init <name> && cd <name> && uv add torch"),
    T("ai", "Download a model from Hugging Face", "huggingface-cli download <org>/<model> --local-dir models/<model>"),
    T("ai", "TensorBoard for a run folder", "tensorboard --logdir runs --port 6006"),
    T("ai", "Run a training script that survives logout", "nohup python train.py > train.log 2>&1 &", platform="linux"),
    # Data engineering
    T("data-eng", "Query a CSV or Parquet file with SQL",
      "duckdb -c \"SELECT * FROM '<file>' LIMIT 20\""),
    T("data-eng", "Parquet schema", "duckdb -c \"DESCRIBE SELECT * FROM '<file>.parquet'\""),
    T("data-eng", "Convert CSV to Parquet", "duckdb -c \"COPY (SELECT * FROM '<file>.csv') TO '<file>.parquet'\""),
    T("data-eng", "Pretty-print JSON", "jq . <file>.json"),
    T("data-eng", "Pick fields from JSON lines", "jq -c '{id, name}' <file>.jsonl"),
    T("data-eng", "PostgreSQL: connect", "psql -h <host> -U <user> -d <database>"),
    T("data-eng", "PostgreSQL: table sizes",
      "psql -c \"SELECT relname, pg_size_pretty(pg_total_relation_size(relid)) FROM pg_catalog.pg_statio_user_tables ORDER BY pg_total_relation_size(relid) DESC LIMIT 20\""),
    T("data-eng", "Count lines in a large file", "wc -l <file>"),
    T("data-eng", "First rows of a CSV as a table", "head -20 <file>.csv | column -s, -t"),
    # Data science
    T("data-sci", "Start JupyterLab", "uv run --with jupyterlab jupyter lab"),
    T("data-sci", "Quick look at a dataset",
      "python -c \"import pandas as pd; df = pd.read_csv('<file>.csv'); print(df.shape); print(df.describe(include='all').T)\""),
    T("data-sci", "Missing values per column",
      "python -c \"import pandas as pd; print(pd.read_csv('<file>.csv').isna().sum().sort_values(ascending=False))\""),
    T("data-sci", "Freeze the environment", "uv pip freeze > requirements.txt"),
    T("data-sci", "Render a notebook to HTML", "uv run --with nbconvert jupyter nbconvert --to html <notebook>.ipynb"),
    # Cybersecurity (defensive and authorised testing)
    T("security", "Listening services on this machine", "ss -tulpn", SECURITY_NOTICE, "linux"),
    T("security", "Listening services on this machine",
      "Get-NetTCPConnection -State Listen | Sort-Object LocalPort", SECURITY_NOTICE, "windows"),
    T("security", "Scan your own host for open ports (authorised only)", "nmap -sV -T3 <your_host>", SECURITY_NOTICE),
    T("security", "Discover devices on your own network (authorised only)", "nmap -sn <your_subnet>/24", SECURITY_NOTICE),
    T("security", "Check a TLS certificate and its expiry",
      "openssl s_client -connect <host>:443 -servername <host> </dev/null 2>/dev/null | openssl x509 -noout -subject -dates"),
    T("security", "File hash (verify a download)", "sha256sum <file>", platform="linux"),
    T("security", "File hash (verify a download)", "Get-FileHash <file> -Algorithm SHA256", platform="windows"),
    T("security", "Verify a signature", "gpg --verify <file>.sig <file>"),
    T("security", "Failed SSH logins", "journalctl -u ssh --since today | grep -i 'failed'", platform="linux"),
    T("security", "Recent failed Windows sign-ins (administrator)",
      "Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4625} -MaxEvents 20", platform="windows"),
    T("security", "Files changed in the last day", "find <dir> -type f -mtime -1 -ls", platform="linux"),
    T("security", "SUID programs (privilege review)", "find / -perm -4000 -type f 2>/dev/null", SECURITY_NOTICE, "linux"),
    T("security", "Security audit of this system", "sudo lynis audit system", "Lynis: open-source hardening audit",
      "linux"),
    T("security", "Secrets accidentally committed to git", "gitleaks detect --source . --verbose",
      "gitleaks scans the repository history for keys and passwords"),
    T("security", "Known vulnerabilities in Python dependencies", "uvx pip-audit"),
    T("security", "Generate a strong random password", "openssl rand -base64 24"),
    # IT project management
    T("pm", "Commits this week by author", "git shortlog -sn --since='1 week ago'"),
    T("pm", "Release notes since the last tag",
      "git log $(git describe --tags --abbrev=0)..HEAD --pretty='- %s (%an)'"),
    T("pm", "Open pull requests", "gh pr list --state open"),
    T("pm", "Open issues assigned to me", "gh issue list --assignee @me"),
    T("pm", "Issues by label", "gh issue list --label <label>"),
    T("pm", "Work in progress notes in the code", "git grep -n -E 'TODO|FIXME|HACK'"),
    T("pm", "Lines changed this month", "git log --since='1 month ago' --shortstat --pretty=tformat: | awk '{a+=$4; d+=$6} END {print a\" added, \"d\" deleted\"}'"),
    T("pm", "Activity per day this month", "git log --since='1 month ago' --date=short --pretty='%ad' | sort | uniq -c"),
)


def for_platform(platform: str) -> list[Tool]:
    kind = "windows" if platform == "win32" else "linux"
    return [t for t in TOOLS if t.platform in ("any", kind)]


def search(tools: list[Tool], query: str, profile: str | None = None) -> list[Tool]:
    """Every word of the query must appear in the field, title or command. The profile's field comes first."""
    words = query.lower().split()
    hits = [t for t in tools
            if all(w in f"{FIELDS[t.field]} {t.field} {t.title} {t.command}".lower() for w in words)]
    order = list(FIELDS)
    return sorted(hits, key=lambda t: (t.field != profile, order.index(t.field)))


def placeholders(command: str) -> list[str]:
    import re

    return list(dict.fromkeys(re.findall(r"<([a-z_]+)>", command)))      # each name once, in order


_SAFE = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._/:@%+=,-~*")


def quote(value: str) -> str:
    """Quote a typed value so it stays one argument: single quotes work in bash, zsh and PowerShell.

    Control characters are removed first, so a value can never add a newline (run) or an escape sequence.
    """
    value = "".join(c for c in value if c.isprintable())
    if value and all(c in _SAFE for c in value):
        return value
    return "'" + value.replace("'", "") + "'"     # a quote inside would end the quoting; it is dropped


def fill(command: str, name: str, value: str) -> str:
    """Replace every <name> with value, safely.

    Inside existing quotes ('<file>' in SQL, "<container>"), the value is inserted without characters that
    could end those quotes; elsewhere it is quoted as one argument.
    """
    clean = "".join(c for c in value if c.isprintable())
    token = f"<{name}>"
    out, i = [], 0
    while (j := command.find(token, i)) != -1:
        before = command[j - 1] if j else ""
        after = command[j + len(token)] if j + len(token) < len(command) else ""
        if before in "'\"" and after == before:
            out.append(command[i:j] + clean.replace(before, "").replace("\\", ""))
        else:
            out.append(command[i:j] + quote(clean))
        i = j + len(token)
    out.append(command[i:])
    return "".join(out)
