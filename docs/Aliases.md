# Aliases

mindas terminal ships a set of short commands and helper functions for **bash/zsh** and **PowerShell**. They
are **opt-in**: the app never edits your shell profile. You print them, read them, and add them yourself.

## Try, then keep

```bash
# bash or zsh
mindas-terminal --aliases bash | less          # read first
eval "$(mindas-terminal --aliases bash)"       # use in this shell only
echo 'eval "$(mindas-terminal --aliases bash)"' >> ~/.bashrc     # keep
```

```powershell
# PowerShell
mindas-terminal --aliases powershell | more
mindas-terminal --aliases powershell | Out-String | Invoke-Expression
Add-Content $PROFILE 'mindas-terminal --aliases powershell | Out-String | Invoke-Expression'
```

To stop using them, remove that line. To freeze a reviewed copy instead of loading them each time:
`mindas-terminal --aliases bash > ~/.mindas-aliases.sh` and `source ~/.mindas-aliases.sh` from your profile.

## Linux habits on Windows

With `alias_style = "linux"` (the default), the PowerShell set adds Linux command names: `touch`, `which`,
`grep`, `head`, `tail`, `tailf`, `wc`, `df`, `du`, `free`, `uptime`, `uname`, `nproc`, `top`, `pkill`,
`ifconfig`, `env`, `export`, `man`, `ln`, `unzip`, `open`, `sudo`. They replace PowerShell's own aliases of the
same name where those exist.

Prefer pure PowerShell? Use `--alias-style native` or `alias_style = "native"` in the settings file.

In Git Bash and on Linux these names are the real commands, so nothing is added.

## Highlights

| Group | Examples |
|---|---|
| Navigation | `..`, `...`, `up 3`, `mkcd dir`, `cdg` (repository top), `bm name` / `go name` bookmarks |
| Files | `ll`, `lt`, `lsize`, `ff name`, `ft text`, `bak file`, `extract archive`, `cpv` (copy with progress), `count` |
| Safety | `rmi`, `cpi`, `mvi` (ask first), `trash` (recoverable delete) |
| System | `psg name`, `ports`, `meminfo`, `diskinfo`, `path`, `h text` (history search), `now`, `reload` |
| Network | `myip`, `localip`, `serve` (this folder on localhost only), `headers url`, `certexp host` |
| Git | `gs`, `gl`, `gd`, `gds`, `gco`, `gcb`, `gundo`, `gwip`, `gclean` |
| DevOps | `dps`, `dlog`, `dsh`, `dclean`, `k`, `kgp`, `kbad`, `kns`, `tfp` |
| HPC | `sq`, `sgpu`, `sacct1`, `sfree` |
| AI and data | `gpu`, `gpuw`, `torchok`, `venv`, `json`, `csvhead`, `sql` |
| Security | `sha file`, `genpass`, `listening`, `lastfail` |

The complete table is in the [Aliases Reference](Aliases-Reference). In bash, `malias` lists them.

## Safety notes

- `serve` binds to `127.0.0.1`, so the folder is not shared with your network. Change it deliberately if you
  need that.
- `genpass` uses cryptographic randomness (`openssl rand` on bash, the .NET secure generator on PowerShell).
- `myip` is the only helper that contacts an outside service (ifconfig.me); its description says so.
- `gwip` uses `--no-verify` on purpose for quick local saves; do not push such commits without review.
- Nothing deletes without asking except commands you call explicitly (`dclean`, `gclean`), and those only
  remove stopped containers, dangling images and branches that are already merged.
