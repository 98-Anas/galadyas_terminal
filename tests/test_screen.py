import pyte

from mindas_terminal.widget import TolerantScreen


def feed(screen, data):
    pyte.Stream(screen).feed(data)


def test_alternate_screen_restores_shell_screen():
    s = TolerantScreen(20, 5)
    feed(s, "prompt$ ")
    feed(s, "\x1b[?1049h" + "VIMTEXT")
    assert "VIMTEXT" in s.display[0] and "prompt" not in s.display[0]
    feed(s, "\x1b[?1049l")
    assert s.display[0].startswith("prompt$") and "VIMTEXT" not in "".join(s.display)


def test_private_sgr_is_ignored():
    s = TolerantScreen(20, 5)
    feed(s, "\x1b[>4;1mok")
    assert s.display[0].startswith("ok")
