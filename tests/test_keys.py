from mindas_terminal.keys import encode


def test_special_keys():
    assert encode("enter", "\r") == "\r"
    assert encode("up", None) == "\x1b[A"
    assert encode("up", None, app_cursor=True) == "\x1bOA"


def test_ctrl_and_alt():
    assert encode("ctrl+c", None) == "\x03"
    assert encode("alt+x", "x") == "\x1bx"


def test_printable_and_unknown():
    assert encode("a", "a") == "a"
    assert encode("ctrl+shift+f13", None) is None
