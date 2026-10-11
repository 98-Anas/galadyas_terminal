# Autocomplete

Type as usual. After two characters, a **faint suggestion** appears after the cursor. Ignore it and keep
typing, or accept it.

![Autocomplete](images/autocomplete.png)

| Key | Action |
|---|---|
| Right arrow or End | Accept the whole suggestion |
| Alt+Right | Accept the next word only |
| Anything else | Ignore it; the suggestion updates as you type |

The suggestion is only typed for you; nothing runs until you press Enter.

## Where suggestions come from

In this order:

1. **Your history**, ranked by *frecency*: commands you use often and recently come first. A command from
   last week counts half as much as one from today.
2. **Common commands** across fields: git, docker, kubectl, terraform, Slurm, Python, uv, system tools.
3. **Toolkit commands** without placeholders.

Your shell's own completion still works: `Tab` goes to the shell as always.

## Did you mean

Mistype a command and the shell answers `command not found` (bash) or `is not recognized` (PowerShell,
cmd). galadyas terminal looks for the closest command you use, or a common one, and offers the corrected line:

```
$ gti status
bash: gti: command not found
$ git status            <- shown faint; press Right arrow to accept
```

Corrections only cover small typos (one or two letters, including swapped letters), so they are rarely wrong.

## When there is no suggestion

Suggestions pause, rather than guess, when galadyas terminal cannot be sure what is on the command line:

- after cursor keys, Tab completion or history search (Up, Ctrl+R) changed the line;
- inside full-screen programs (vim, less, htop);
- in copy mode.

They resume at the next prompt (after Enter, Ctrl+C or Ctrl+U).

## Privacy

- History is stored only on your machine, next to the settings file (`history.tsv`), readable by your user
  only. It is never sent anywhere.
- Commands that start with a **space**, and commands that look like they contain **secrets**, are never
  stored: `password=`, `--token`, API keys (AWS, GitHub, Slack, `sk-...`), `user:password@` in URLs,
  `mysql -pSECRET`, `export SOMETHING_KEY=...`.
- `remember_history = false` in the settings keeps history in memory for the session only.
- *Forget history* in the command palette deletes it.

See [Security](Security) for the full threat model.
