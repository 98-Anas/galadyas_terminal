"""Autocomplete and "did you mean": pure logic, no UI.

- `LineTracker` follows what the user types on the current command line (it never reads the screen), and
  gives up as soon as it cannot be sure (cursor keys, history keys, full-screen programs), so a suggestion
  is only shown when it is certainly right about the text before it.
- `History` remembers commands with frecency (frequent and recent first). Commands that look like they
  contain secrets, and commands typed with a leading space, are never remembered.
- `suggest` finds the best completion for a prefix from history, aliases, toolkit commands and common tools.
- `did_you_mean` finds the closest known command to a mistyped one.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field

# Commands people type everywhere; completed after history, before toolkit commands.
COMMON = (
    "git status", "git add -A", "git commit -m ''", "git push", "git pull", "git log --oneline --graph -20",
    "git diff", "git switch ", "git checkout -b ", "git stash", "git clone ", "git remote -v",
    "docker ps", "docker images", "docker compose up -d", "docker compose down", "docker logs -f ",
    "docker exec -it ", "docker run --rm -it ", "docker build -t ",
    "kubectl get pods", "kubectl get pods -A", "kubectl describe pod ", "kubectl logs -f ", "kubectl apply -f ",
    "kubectl get svc", "kubectl config get-contexts",
    "terraform init", "terraform plan", "terraform apply", "ansible-playbook ",
    "python -m venv .venv", "python -m pip install ", "pip install -r requirements.txt", "uv sync", "uv run ",
    "uv add ", "pytest -q", "jupyter lab", "nvidia-smi", "htop", "top",
    "ls -la", "cd ..", "cd ~", "mkdir -p ", "cat ", "less ", "tail -f ", "grep -rn ", "find . -name ",
    "du -sh *", "df -h", "free -h", "ps aux", "ssh ", "scp ", "rsync -avh --progress ", "curl -sSI ",
    "tar -czvf ", "tar -xzvf ", "chmod +x ", "sudo apt update", "sudo apt install ", "systemctl status ",
    "journalctl -u ", "squeue -u $USER", "sbatch ", "srun --pty bash", "sinfo", "scancel ", "sacct",
    "module avail", "module load ", "nmap -sV ", "openssl s_client -connect ", "sha256sum ",
    "Get-Process", "Get-Service", "Get-ChildItem", "Set-Location ", "Test-NetConnection ",
)

# Anything that looks like a secret is never stored or suggested.
SECRET = re.compile(
    r"(pass(word|wd)?|secret|token|api[_-]?key|private[_-]?key|authorization|bearer)\s*[=:]"
    r"|--(password|token|secret)(\s|=)\S"
    r"|\b(AKIA|ASIA)[0-9A-Z]{16}\b"                       # AWS access key IDs
    r"|\bgh[pousr]_[A-Za-z0-9]{20,}"                      # GitHub tokens
    r"|\bsk-[A-Za-z0-9_-]{20,}"                           # common API key shape
    r"|\bxox[abpr]-[A-Za-z0-9-]{10,}"                     # Slack tokens
    r"|://[^/\s:@]+:[^/\s@]+@"                            # user:password@ in URLs
    r"|(^|\s)-p\S+"                                        # mysql -pSECRET
    r"|\bexport\s+\w*(KEY|TOKEN|SECRET|PASS)\w*=",
    re.IGNORECASE)

NOT_FOUND = re.compile(
    r"(?:bash|zsh|sh)?:?\s*(?:line \d+: )?([\w.+-]+): (?:command )?not found"
    r"|'([\w.+-]+)' is not recognized as"                 # cmd and PowerShell
    r"|The term '([\w.+-]+)' is not recognized")


def is_sensitive(command: str) -> bool:
    return command.startswith(" ") or bool(SECRET.search(command))


@dataclass
class Entry:
    count: int = 0
    last: float = 0.0

    def score(self, now: float) -> float:
        """Frecency: frequent and recent commands first; a week-old command counts half as much."""
        age_days = max(now - self.last, 0) / 86_400
        return self.count / (1 + age_days / 7)


@dataclass
class History:
    limit: int = 5000
    entries: dict[str, Entry] = field(default_factory=dict)

    def add(self, command: str, now: float | None = None) -> bool:
        """Remember a command; returns False when it is not stored (empty, too long, or sensitive)."""
        if not command.strip() or len(command) > 1000 or is_sensitive(command):
            return False
        command = command.strip()
        e = self.entries.setdefault(command, Entry())
        e.count += 1
        e.last = time.time() if now is None else now
        if len(self.entries) > self.limit:                      # forget the least valuable
            t = time.time() if now is None else now
            worst = min(self.entries, key=lambda c: self.entries[c].score(t))
            del self.entries[worst]
        return True

    def ranked(self, now: float | None = None) -> list[str]:
        t = time.time() if now is None else now
        return sorted(self.entries, key=lambda c: self.entries[c].score(t), reverse=True)

    # storage: one command per line, "count<TAB>last<TAB>command"
    def dumps(self) -> str:
        return "".join(f"{e.count}\t{e.last:.0f}\t{c}\n" for c, e in self.entries.items())

    @classmethod
    def loads(cls, text: str, limit: int = 5000) -> History:
        h = cls(limit=limit)
        for line in text.splitlines():
            parts = line.split("\t", 2)
            if len(parts) == 3 and parts[0].isdigit() and not is_sensitive(parts[2]):
                try:
                    h.entries[parts[2]] = Entry(int(parts[0]), float(parts[1]))
                except ValueError:
                    continue
        return h


def suggest(prefix: str, history: list[str], extra: tuple[str, ...] | list[str] = ()) -> str | None:
    """The best full command starting with prefix (history first), or None. Needs two characters."""
    if len(prefix.strip()) < 2 or "\n" in prefix:
        return None
    for source in (history, COMMON, extra):
        for cmd in source:
            if cmd.startswith(prefix) and cmd != prefix:
                return cmd
    return None


def next_word(prefix: str, completion: str) -> str:
    """The part of completion after prefix, up to and including the next word (Alt+Right)."""
    rest = completion[len(prefix):]
    m = re.match(r"\s*\S+\s?", rest)
    return m.group(0) if m else rest


def _distance(a: str, b: str, limit: int = 3) -> int:
    """Damerau-Levenshtein distance (with transpositions), stopping early past limit."""
    if abs(len(a) - len(b)) > limit:
        return limit + 1
    prev2: list[int] | None = None
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            v = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb))
            if prev2 is not None and i > 1 and j > 1 and ca == b[j - 2] and a[i - 2] == cb:
                v = min(v, prev2[j - 2] + 1)
            cur.append(v)
        prev2, prev = prev, cur
    return prev[-1]


def known_programs(history: list[str], extra: tuple[str, ...] | list[str] = ()) -> list[str]:
    names = []
    for cmd in [*history, *COMMON, *extra]:
        word = cmd.split(" ", 1)[0]
        if word and word not in names and re.fullmatch(r"[\w.+-]+", word):
            names.append(word)
    return names


def did_you_mean(word: str, programs: list[str]) -> str | None:
    """Closest known program name to a mistyped one, or None when nothing is close."""
    best, best_d = None, 3
    for p in programs:
        if p == word:
            return None
        d = _distance(word.lower(), p.lower())
        limit = 1 if len(word) <= 4 else 2
        if d <= limit and d < best_d:
            best, best_d = p, d
    return best


def not_found(text: str) -> str | None:
    """The command name from a 'command not found' message, if any."""
    m = NOT_FOUND.search(text)
    return next((g for g in m.groups() if g), None) if m else None


class LineTracker:
    """Follows the command line as typed. `text` is None while unsure (then nothing is suggested)."""

    def __init__(self) -> None:
        self.text: str | None = ""

    def reset(self) -> None:
        self.text = ""

    def lost(self) -> None:
        self.text = None

    def typed(self, data: str) -> str | None:
        """Update with what was sent to the shell; returns a completed command line on Enter."""
        if data == "\r":
            line, self.text = self.text, ""
            return line
        if self.text is None:
            if data in ("\x03", "\x15"):                  # Ctrl+C, Ctrl+U: the line is empty again
                self.text = ""
            return None
        if data in ("\x7f", "\x08"):
            self.text = self.text[:-1]
        elif data in ("\x03", "\x15"):
            self.text = ""
        elif data == "\x17":                                # Ctrl+W: delete the previous word
            self.text = re.sub(r"\S+\s*$", "", self.text)
        elif data.isprintable():
            self.text += data
        else:                                               # cursor keys, Tab, Ctrl+R, escape sequences
            self.text = None
        return None
