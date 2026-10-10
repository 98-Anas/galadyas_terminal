import os
import sys

import pytest

from mindas_terminal import config, suggest


def test_line_tracker_follows_typing_and_gives_up_when_unsure():
    t = suggest.LineTracker()
    for ch in "git sta":
        t.typed(ch)
    assert t.text == "git sta"
    t.typed("\x7f")
    assert t.text == "git st"
    t.typed("\x17")                          # Ctrl+W
    assert t.text == "git "
    t.typed("\x1b[A")                         # Up: history replaced the line
    assert t.text is None
    assert t.typed("\r") is None and t.text == ""
    for ch in "ls":
        t.typed(ch)
    assert t.typed("\r") == "ls"


def test_suggest_prefers_history_then_common():
    hist = ["git push origin feature", "ls -la"]
    assert suggest.suggest("git p", hist) == "git push origin feature"
    assert suggest.suggest("kubectl get p", []) == "kubectl get pods"
    assert suggest.suggest("g", hist) is None                     # needs two characters
    assert suggest.suggest("ls -la", hist) is None                # nothing to add
    assert suggest.next_word("git p", "git push origin feature") == "ush "


def test_history_frecency_and_secret_filter():
    h = suggest.History()
    now = 1_000_000.0
    h.add("old command", now - 30 * 86_400)
    for _ in range(2):
        h.add("recent command", now)
    assert h.ranked(now)[0] == "recent command"
    for secret in (" ls with leading space", "mysql -u root -pHunter2", "curl -H 'Authorization: Bearer abc'",
                   "export API_KEY=abc", "git clone https://user:pw@host/repo", "aws AKIAABCDEFGHIJKLMNOP",
                   "echo ghp_abcdefghijklmnopqrstuvwxyz123456", "tool --token xyz", "password=hunter2"):
        assert not h.add(secret, now), secret
    assert set(h.entries) == {"old command", "recent command"}


def test_history_round_trip_drops_planted_secrets():
    h = suggest.History.loads("3\t100\tgit status\n1\t100\tpassword=x\nbroken line\n")
    assert list(h.entries) == ["git status"]
    assert suggest.History.loads(h.dumps()).entries.keys() == h.entries.keys()


def test_history_is_bounded():
    h = suggest.History(limit=3)
    for i in range(10):
        h.add(f"cmd {i}", 1000.0 + i)
    assert len(h.entries) == 3


def test_did_you_mean():
    progs = suggest.known_programs(["kubectl get pods"], ())
    assert suggest.did_you_mean("gti", progs) == "git"
    assert suggest.did_you_mean("kubeclt", progs) == "kubectl"
    assert suggest.did_you_mean("git", progs) is None             # already right
    assert suggest.did_you_mean("zzzzzz", progs) is None          # nothing close


def test_not_found_messages():
    assert suggest.not_found("bash: gti: command not found") == "gti"
    assert suggest.not_found("'gti' is not recognized as an internal or external command") == "gti"
    assert suggest.not_found("gti : The term 'gti' is not recognized as the name of a cmdlet") == "gti"
    assert suggest.not_found("all good") is None


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX permissions")
def test_history_file_is_private(tmp_path):
    target = tmp_path / "h.tsv"
    config.save_private(target, "1\t1\tls\n")
    assert oct(os.stat(target).st_mode & 0o777) == "0o600"
