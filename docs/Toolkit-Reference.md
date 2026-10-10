# Toolkit Reference

Generated from `src/mindas_terminal/toolkit.py`. Open the toolkits with `prefix g` (or `Toolkits` in the command palette), type a few words, press Enter.

Commands are **inserted at the prompt and never run**. Values you type for `<placeholders>` are quoted so they stay one argument. Platform `any` means both Windows (Git Bash or PowerShell) and Linux.

> **Ethical use.** Use these only on systems you own or are authorised in writing to test. Unauthorised scanning or access is illegal in most countries.

109 commands in 11 fields.

| Field | Profile name |
|---|---|
| [Linux and IT support](#linux) | `linux` |
| [Windows administration](#windows) | `windows` |
| [Networking](#network) | `network` |
| [Git and code review](#git) | `git` |
| [DevOps and cloud](#devops) | `devops` |
| [HPC and Slurm](#hpc) | `hpc` |
| [AI and ML engineering](#ai) | `ai` |
| [Data engineering](#data-eng) | `data-eng` |
| [Data science](#data-sci) | `data-sci` |
| [Cybersecurity (ethical)](#security) | `security` |
| [IT project management](#pm) | `pm` |

<a id="linux"></a>

## Linux and IT support

| Task | Command | Platform |
|---|---|---|
| Disk usage by folder, largest first | `du -h --max-depth=1 . \| sort -hr \| head -20` | any |
| Free disk space per filesystem | `df -h` | any |
| Largest files under a folder | `find <dir> -type f -printf '%s %p\n' \| sort -nr \| head -20` | any |
| Follow a log file | `tail -f <file>` | any |
| Recent system errors | `journalctl -p err -b --no-pager \| tail -50` | linux |
| Service status and recent logs | `systemctl status <service> --no-pager -l` | linux |
| Who is using a port | `ss -ltnp \| grep :<port>` | linux |
| Memory overview | `free -h` | linux |
| Find text in files | `grep -rn --color '<text>' <dir>` | any |
| Archive a folder (tar.gz)<br><sub>c create, z gzip, v list files, f file name</sub> | `tar -czvf <name>.tar.gz <dir>` | any |
| Extract a tar.gz | `tar -xzvf <name>.tar.gz -C <dir>` | any |
| Copy a folder with progress, resumable<br><sub>a keeps permissions and times; the trailing / copies the contents</sub> | `rsync -avh --progress <src>/ <dest>/` | any |
| Change owner recursively | `sudo chown -R <user>:<group> <dir>` | linux |

<a id="windows"></a>

## Windows administration

| Task | Command | Platform |
|---|---|---|
| System summary | `Get-ComputerInfo \| Select-Object OsName, OsVersion, CsTotalPhysicalMemory` | windows |
| Top processes by memory | `Get-Process \| Sort-Object WS -Descending \| Select-Object -First 15` | windows |
| Services that are stopped but set to automatic | `Get-Service \| Where-Object {$_.StartType -eq 'Automatic' -and $_.Status -ne 'Running'}` | windows |
| Recent system errors | `Get-WinEvent -LogName System -MaxEvents 50 \| Where-Object LevelDisplayName -eq 'Error'` | windows |
| Network configuration | `ipconfig /all` | windows |
| Flush DNS cache | `ipconfig /flushdns` | windows |
| Check system files (administrator) | `sfc /scannow` | windows |
| Repair the Windows image (administrator) | `DISM /Online /Cleanup-Image /RestoreHealth` | windows |
| Installed updates | `Get-HotFix \| Sort-Object InstalledOn -Descending \| Select-Object -First 10` | windows |
| Who is using a port | `Get-NetTCPConnection -LocalPort <port> \| Select-Object OwningProcess, State` | windows |

<a id="network"></a>

## Networking

| Task | Command | Platform |
|---|---|---|
| Is a host reachable | `ping -c 4 <host>` | linux |
| Is a host reachable | `ping -n 4 <host>` | windows |
| Path to a host | `traceroute <host>` | linux |
| Path to a host | `tracert <host>` | windows |
| DNS lookup | `nslookup <domain>` | any |
| Is a TCP port open | `nc -zv <host> <port>` | linux |
| Is a TCP port open | `Test-NetConnection <host> -Port <port>` | windows |
| HTTP response headers | `curl -sSI <url>` | any |
| Download a file | `curl -fLO <url>` | any |
| Listening ports | `ss -tulpn` | linux |
| Public IP address | `curl -s https://ifconfig.me` | any |

<a id="git"></a>

## Git and code review

| Task | Command | Platform |
|---|---|---|
| Compact history graph | `git log --oneline --graph --decorate -20` | any |
| What changed, staged and unstaged | `git status -sb && git diff --stat` | any |
| Undo the last commit, keep the changes | `git reset --soft HEAD~1` | any |
| Find the commit that broke something | `git bisect start && git bisect bad && git bisect good <commit>` | any |
| Who changed each line | `git blame -w <file>` | any |
| Search history for a string | `git log -S '<text>' --oneline` | any |
| Stash work including new files | `git stash push -u -m '<message>'` | any |
| Delete merged local branches | `git branch --merged \| grep -vE '^\*\|main\|master' \| xargs -r git branch -d` | any |

<a id="devops"></a>

## DevOps and cloud

| Task | Command | Platform |
|---|---|---|
| Running containers | `docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'` | any |
| Run a container with a port and a folder<br><sub>--rm removes it on exit; -v mounts the current folder</sub> | `docker run --rm -it -p <host_port>:<container_port> -v "$PWD":/work -w /work <image>` | any |
| Container logs, follow | `docker logs -f --tail 100 <container>` | any |
| Shell inside a container | `docker exec -it <container> sh` | any |
| Disk used by Docker | `docker system df` | any |
| Compose: start in background | `docker compose up -d` | any |
| Kubernetes: pods that are not running | `kubectl get pods -A --field-selector=status.phase!=Running` | any |
| Kubernetes: logs of a pod | `kubectl logs -f <pod> -n <namespace>` | any |
| Kubernetes: describe a failing pod | `kubectl describe pod <pod> -n <namespace>` | any |
| Kubernetes: switch namespace | `kubectl config set-context --current --namespace=<namespace>` | any |
| Terraform: review a plan | `terraform init && terraform plan -out=tfplan` | any |
| Terraform: apply the reviewed plan | `terraform apply tfplan` | any |
| Ansible: check mode (dry run) | `ansible-playbook -i <inventory> <playbook>.yml --check --diff` | any |

<a id="hpc"></a>

## HPC and Slurm

| Task | Command | Platform |
|---|---|---|
| My jobs in the queue | `squeue -u $USER` | any |
| Submit a batch job | `sbatch <job>.sbatch` | any |
| Interactive GPU session | `srun --gres=gpu:1 --cpus-per-task=8 --mem=32G --time=02:00:00 --pty bash` | any |
| Cancel a job | `scancel <jobid>` | any |
| Accounting for finished jobs | `sacct -u $USER --starttime today --format=JobID,JobName,State,Elapsed,MaxRSS` | any |
| Partitions and free nodes | `sinfo -o '%P %a %l %D %t'` | any |
| Why a job is pending | `squeue -j <jobid> -o '%i %T %r'` | any |
| Available software modules | `module avail` | any |
| Copy results back from a cluster | `rsync -avh --progress <user>@<cluster>:<path> ./` | any |

<a id="ai"></a>

## AI and ML engineering

| Task | Command | Platform |
|---|---|---|
| GPU use, refresh every second | `nvidia-smi -l 1` | any |
| GPU processes | `nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv` | any |
| Is PyTorch using the GPU | `python -c "import torch; print(torch.__version__, torch.cuda.is_available())"` | any |
| New project environment with uv | `uv init <name> && cd <name> && uv add torch` | any |
| Download a model from Hugging Face | `huggingface-cli download <org>/<model> --local-dir models/<model>` | any |
| TensorBoard for a run folder | `tensorboard --logdir runs --port 6006` | any |
| Run a training script that survives logout | `nohup python train.py > train.log 2>&1 &` | linux |

<a id="data-eng"></a>

## Data engineering

| Task | Command | Platform |
|---|---|---|
| Query a CSV or Parquet file with SQL | `duckdb -c "SELECT * FROM '<file>' LIMIT 20"` | any |
| Parquet schema | `duckdb -c "DESCRIBE SELECT * FROM '<file>.parquet'"` | any |
| Convert CSV to Parquet | `duckdb -c "COPY (SELECT * FROM '<file>.csv') TO '<file>.parquet'"` | any |
| Pretty-print JSON | `jq . <file>.json` | any |
| Pick fields from JSON lines | `jq -c '{id, name}' <file>.jsonl` | any |
| PostgreSQL: connect | `psql -h <host> -U <user> -d <database>` | any |
| PostgreSQL: table sizes | `psql -c "SELECT relname, pg_size_pretty(pg_total_relation_size(relid)) FROM pg_catalog.pg_statio_user_tables ORDER BY pg_total_relation_size(relid) DESC LIMIT 20"` | any |
| Count lines in a large file | `wc -l <file>` | any |
| First rows of a CSV as a table | `head -20 <file>.csv \| column -s, -t` | any |

<a id="data-sci"></a>

## Data science

| Task | Command | Platform |
|---|---|---|
| Start JupyterLab | `uv run --with jupyterlab jupyter lab` | any |
| Quick look at a dataset | `python -c "import pandas as pd; df = pd.read_csv('<file>.csv'); print(df.shape); print(df.describe(include='all').T)"` | any |
| Missing values per column | `python -c "import pandas as pd; print(pd.read_csv('<file>.csv').isna().sum().sort_values(ascending=False))"` | any |
| Freeze the environment | `uv pip freeze > requirements.txt` | any |
| Render a notebook to HTML | `uv run --with nbconvert jupyter nbconvert --to html <notebook>.ipynb` | any |

<a id="security"></a>

## Cybersecurity (ethical)

| Task | Command | Platform |
|---|---|---|
| Listening services on this machine | `ss -tulpn` | linux |
| Listening services on this machine | `Get-NetTCPConnection -State Listen \| Sort-Object LocalPort` | windows |
| Scan your own host for open ports (authorised only) | `nmap -sV -T3 <your_host>` | any |
| Discover devices on your own network (authorised only) | `nmap -sn <your_subnet>/24` | any |
| Check a TLS certificate and its expiry | `openssl s_client -connect <host>:443 -servername <host> </dev/null 2>/dev/null \| openssl x509 -noout -subject -dates` | any |
| File hash (verify a download) | `sha256sum <file>` | linux |
| File hash (verify a download) | `Get-FileHash <file> -Algorithm SHA256` | windows |
| Verify a signature | `gpg --verify <file>.sig <file>` | any |
| Failed SSH logins | `journalctl -u ssh --since today \| grep -i 'failed'` | linux |
| Recent failed Windows sign-ins (administrator) | `Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4625} -MaxEvents 20` | windows |
| Files changed in the last day | `find <dir> -type f -mtime -1 -ls` | linux |
| SUID programs (privilege review) | `find / -perm -4000 -type f 2>/dev/null` | linux |
| Security audit of this system<br><sub>Lynis: open-source hardening audit</sub> | `sudo lynis audit system` | linux |
| Secrets accidentally committed to git<br><sub>gitleaks scans the repository history for keys and passwords</sub> | `gitleaks detect --source . --verbose` | any |
| Known vulnerabilities in Python dependencies | `uvx pip-audit` | any |
| Generate a strong random password | `openssl rand -base64 24` | any |

<a id="pm"></a>

## IT project management

| Task | Command | Platform |
|---|---|---|
| Commits this week by author | `git shortlog -sn --since='1 week ago'` | any |
| Release notes since the last tag | `git log $(git describe --tags --abbrev=0)..HEAD --pretty='- %s (%an)'` | any |
| Open pull requests | `gh pr list --state open` | any |
| Open issues assigned to me | `gh issue list --assignee @me` | any |
| Issues by label | `gh issue list --label <label>` | any |
| Work in progress notes in the code | `git grep -n -E 'TODO\|FIXME\|HACK'` | any |
| Lines changed this month | `git log --since='1 month ago' --shortstat --pretty=tformat: \| awk '{a+=$4; d+=$6} END {print a" added, "d" deleted"}'` | any |
| Activity per day this month | `git log --since='1 month ago' --date=short --pretty='%ad' \| sort \| uniq -c` | any |
