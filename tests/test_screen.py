import pyte

from mindas_terminal.screen import TerminalScreen as TolerantScreen, clean_title


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


def test_scrollback_keeps_lines_that_scroll_off():
    s = TolerantScreen(20, 3, scrollback=100)
    feed(s, "\r\n".join(f"line{i}" for i in range(10)))
    assert len(s.history) == 7
    assert s.row_text(s.history[0]) == "line0"
    assert [s.row_text(r) for r in s.snapshot()][-1] == "line9"


def test_scrollback_is_bounded_and_clearable():
    s = TolerantScreen(20, 3, scrollback=5)
    feed(s, "\r\n".join(str(i) for i in range(50)))
    assert len(s.history) == 5
    feed(s, "\x1b[3J")
    assert len(s.history) == 0


def test_alt_screen_does_not_pollute_scrollback():
    s = TolerantScreen(20, 3)
    feed(s, "\x1b[?1049h" + "\r\n".join(str(i) for i in range(20)) + "\x1b[?1049l")
    assert len(s.history) == 0


def test_titles_are_sanitised():
    assert clean_title("ok\x1b[31mred\x07") == "ok[31mred"
    assert len(clean_title("x" * 500)) == 60


def test_hostile_output_cannot_answer_back_or_crash():
    """Device reports, clipboard writes, title tricks and huge parameters must not reach the shell or crash."""
    replies = []
    s = TolerantScreen(40, 10)
    s.reply_sink = replies.append
    hostile = ("\x1b[6n" "\x1b[c" "\x1b[>c" "\x1b]52;c;ZWNobyBwd25lZA==\x07" "\x1b]0;evil\x1b[31m\x07"
               "\x1b[99999999C" "\x1b[99999999;99999999H" "\x1b[?3h" "\x1bP+q544e\x1b\\" "\x1b[8;9999;9999t"
               "\x1b[>4;1m" "\x9b31m" + "A" * 10000)
    pyte.Stream(s).feed(hostile)
    from mindas_terminal.screen import SAFE_REPLY
    assert replies and all(SAFE_REPLY.fullmatch(r) for r in replies)
    assert not any("evil" in r or "52;" in r for r in replies)
    assert "\x1b" not in s.title and "evil" in s.title
    assert s.lines == 10
