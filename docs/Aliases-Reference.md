# Aliases Reference

Generated from `src/galadyas_terminal/aliases.py`. These are **opt-in**: nothing changes in your shell until you add them yourself.

```bash
# bash or zsh: try them in the current shell
eval "$(galadyas-terminal --aliases bash)"
# keep them: add the same line to ~/.bashrc or ~/.zshrc
```

```powershell
# PowerShell: try them in the current session
galadyas-terminal --aliases powershell | Out-String | Invoke-Expression
# keep them: add the same line to $PROFILE
```

`--alias-style linux` (default) also gives PowerShell the Linux command names in the first table, so the same muscle memory works everywhere. `--alias-style native` leaves them out. Type `malias` in bash to list everything.

89 aliases and helper functions.

## Linux command names in PowerShell

| Name | What it does | bash | PowerShell |
|---|---|---|---|
| `touch` | create a file or update its time | built in | yes |
| `which` | where a command comes from | built in | yes |
| `grep` | search text: grep pattern file | built in | yes |
| `head` | first lines: head file 20 | built in | yes |
| `tail` | last lines: tail file 20 | built in | yes |
| `tailf` | follow a file | built in | yes |
| `wc` | count lines, words, characters | built in | yes |
| `df` | disk space | built in | yes |
| `du` | folder size: du path | built in | yes |
| `free` | memory | built in | yes |
| `uptime` | time since boot | built in | yes |
| `uname` | system name and version | built in | yes |
| `nproc` | number of CPUs | built in | yes |
| `top` | top processes by CPU | built in | yes |
| `pkill` | stop processes by name (asks first) | built in | yes |
| `ifconfig` | network addresses | built in | yes |
| `env` | environment variables | built in | yes |
| `export` | set a variable: export NAME=value | built in | yes |
| `man` | help for a command | built in | yes |
| `ln` | symbolic link: ln -s target link | built in | yes |
| `unzip` | extract a zip | built in | yes |
| `open` | open with the default app (xdg-open) | built in | yes |
| `sudo` | run as administrator (new window, asks) | built in | yes |

## Navigation

| Name | What it does | bash | PowerShell |
|---|---|---|---|
| `..` | up one folder | yes | yes |
| `...` | up two folders | yes | yes |
| `up` | up N folders: up 3 | yes | yes |
| `mkcd` | make a folder and enter it | yes | yes |
| `cdg` | go to the top of the git repository | yes | yes |
| `bm` | bookmark this folder as NAME: bm work | yes | no |
| `go` | jump to a bookmark: go work | yes | no |

## Files

| Name | What it does | bash | PowerShell |
|---|---|---|---|
| `ll` | long list, human sizes | yes | yes |
| `lt` | newest files last | yes | yes |
| `lsize` | largest items here | yes | yes |
| `ff` | find files by name: ff report | yes | yes |
| `ft` | find text in files: ft TODO | yes | yes |
| `bak` | timestamped backup copy: bak config.yml | yes | yes |
| `extract` | extract any archive: extract file.tar.gz | yes | yes |
| `cpv` | copy with progress (rsync) | yes | no |
| `count` | files per extension here | yes | no |

## Safety

| Name | What it does | bash | PowerShell |
|---|---|---|---|
| `rmi` | remove, asking for each file | yes | yes |
| `cpi` | copy, asking before overwrite | yes | no |
| `mvi` | move, asking before overwrite | yes | no |
| `trash` | move to ~/.trash instead of deleting | yes | yes |

## System

| Name | What it does | bash | PowerShell |
|---|---|---|---|
| `psg` | find processes: psg python | yes | yes |
| `ports` | listening ports | yes | yes |
| `meminfo` | memory overview | yes | yes |
| `diskinfo` | disk space | yes | yes |
| `path` | PATH, one entry per line | yes | yes |
| `h` | search history: h docker | yes | yes |
| `now` | date and time, ISO format | yes | yes |
| `reload` | reload the shell profile | yes | yes |

## Network

| Name | What it does | bash | PowerShell |
|---|---|---|---|
| `myip` | public IP (asks ifconfig.me) | yes | yes |
| `localip` | local IP addresses | yes | yes |
| `serve` | share this folder on localhost:8000 only | yes | yes |
| `headers` | HTTP response headers: headers https://example.com | yes | yes |
| `certexp` | TLS certificate expiry: certexp example.com | yes | no |

## Git

| Name | What it does | bash | PowerShell |
|---|---|---|---|
| `gs` | short status | yes | yes |
| `gl` | history graph | yes | yes |
| `gd` | unstaged diff | yes | yes |
| `gds` | staged diff | yes | yes |
| `gco` | switch branch | yes | yes |
| `gcb` | new branch | yes | yes |
| `gundo` | undo last commit, keep changes | yes | yes |
| `gwip` | quick work-in-progress commit | yes | yes |
| `gclean` | delete merged branches | yes | no |

## Devops

| Name | What it does | bash | PowerShell |
|---|---|---|---|
| `dps` | running containers | yes | yes |
| `dlog` | follow container logs: dlog web | yes | yes |
| `dsh` | shell in a container: dsh web | yes | yes |
| `dclean` | remove stopped containers and dangling images | yes | no |
| `k` | kubectl | yes | yes |
| `kgp` | pods in the current namespace | yes | yes |
| `kbad` | pods that are not running | yes | no |
| `kns` | switch namespace: kns prod | yes | no |
| `tfp` | terraform plan to a file | yes | no |

## Hpc

| Name | What it does | bash | PowerShell |
|---|---|---|---|
| `sq` | my Slurm jobs | yes | no |
| `sgpu` | interactive GPU shell (1 GPU, 2 hours) | yes | no |
| `sacct1` | today's finished jobs | yes | no |
| `sfree` | partitions and idle nodes | yes | no |

## Ai

| Name | What it does | bash | PowerShell |
|---|---|---|---|
| `gpu` | GPU use | yes | yes |
| `gpuw` | GPU use, refresh every second | yes | yes |
| `torchok` | is PyTorch using the GPU | yes | no |
| `venv` | create or activate .venv here | yes | yes |

## Data

| Name | What it does | bash | PowerShell |
|---|---|---|---|
| `json` | pretty-print JSON from a file or stdin | yes | yes |
| `csvhead` | first rows of a CSV as a table | yes | no |
| `sql` | SQL over CSV/Parquet with DuckDB: sql "select * from 'x.csv'" | yes | no |

## Security

| Name | What it does | bash | PowerShell |
|---|---|---|---|
| `sha` | SHA-256 of a file | yes | yes |
| `genpass` | strong random password | yes | yes |
| `listening` | services listening on this machine | yes | yes |
| `lastfail` | recent failed logins | yes | yes |
