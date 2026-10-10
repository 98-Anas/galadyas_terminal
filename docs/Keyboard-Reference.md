# Keyboard Reference

`prefix` is **Ctrl+B** unless you changed it ([Configuration](Configuration)). Press the prefix, release it,
then the key. Inside the app, `prefix ?` shows this page.

## Tabs

| Keys | Action |
|---|---|
| `prefix c` | New tab with the default shell |
| `prefix n` / `prefix p` | Next / previous tab |
| `prefix 1` ... `prefix 9` | Go to tab 1 to 9 |
| `prefix ,` | Rename the tab (empty name: use the program's title again) |
| `prefix &` | Close the tab and its panes (asks first) |
| Mouse click on a tab | Go to that tab |

## Panes

| Keys | Action |
|---|---|
| `prefix %` or `prefix \|` | Split right (side by side) |
| `prefix "` or `prefix -` | Split down (top and bottom) |
| `prefix` + arrow, or `prefix h` `j` `k` `l` | Move to the pane on the left, below, above, right |
| `prefix o` | Next pane |
| `prefix z` | Zoom the pane to the full tab; again to restore |
| `prefix x` | Close the pane (asks first) |
| `exit` in the shell | Closes its pane; the last pane closes the app |

## Copy mode (vim keys)

Enter with `prefix [`, `Shift+PageUp`, or the mouse wheel.

| Keys | Action |
|---|---|
| `h` `j` `k` `l` or arrows | Left, down, up, right |
| `w` / `b` | Next / previous word |
| `0` / `^` / `$` | Line start / first non-blank / line end |
| `H` / `M` / `L` | Top / middle / bottom of the view |
| `Ctrl+U` / `Ctrl+D` | Half page up / down |
| `Ctrl+B` / `Ctrl+F`, `PageUp` / `PageDown` | Page up / down |
| `Ctrl+Y` / `Ctrl+E` | Scroll the view one line |
| `g` / `G` | Oldest line / newest line |
| `/` text Enter | Search forward |
| `?` text Enter | Search backward |
| `n` / `N` | Next / previous match |
| `v` or `Space` | Start or stop a character selection |
| `V` | Start or stop a line selection |
| `y` or `Enter` | Copy the selection (or the current line) and leave |
| `Esc` | Clear the selection; again to leave |
| `q` | Leave copy mode |

## Tools

| Keys | Action |
|---|---|
| `prefix H` | Home window: open shells and tools with a click |
| `prefix m` | Manual: these pages, offline and searchable |
| `prefix g` | Toolkits: curated commands for your field |
| `Right` / `End` / `Alt+Right` | Accept the autocomplete suggestion / one word of it ([Autocomplete](Autocomplete)) |
| `prefix t` | Task manager |
| `prefix :` or `prefix P` | Command palette |
| `prefix ]` | Paste the text copied last in copy mode |
| `prefix ?` | Keyboard reference |
| `Ctrl+Q` | Quit (asks first when more than one pane is open) |

## Task manager

| Keys | Action |
|---|---|
| `c` `m` `g` `p` `n` | Sort by CPU, memory, GPU, process ID, name (again to reverse) |
| `/` | Filter by name, command, user or process ID |
| `f` | Only processes started from this terminal (toggle) |
| `k` / `K` | Terminate / kill the selected process (asks first) |
| `r` | Refresh now |
| `q` or `Esc` | Close |

## Toolkits

| Keys | Action |
|---|---|
| typing | Filter: every word must match |
| `Up` / `Down` | Move |
| `Enter` | Insert the command at the prompt (it does not run) |
| `Esc` | Close |

## Mouse

| Click | Action |
|---|---|
| A card in the home window | Open that shell or tool |
| A tab | Go to the tab |
| A pane | Focus it |
| `home`, `+tab`, `split`, `zoom`, `tools`, `tasks`, `manual`, `keys` in the status bar | Run that action |
| A page or a link in the manual | Open it (web links are copied, not opened) |
| Mouse wheel in a pane | Copy mode (or arrow keys in full-screen programs) |

## Passing keys through

Every key not listed above goes to the program in the pane, including `Tab`, `Ctrl+C`, `Ctrl+R`, `Ctrl+P`,
function keys and `Alt` combinations. To send the prefix key itself, press it twice.
