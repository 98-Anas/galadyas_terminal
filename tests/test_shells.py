from mindas_terminal import shells


def test_windows_prefers_git_bash():
    git_bash = r"C:\Program Files\Git\bin\bash.exe"
    found = shells.detect("win32", exists=lambda p: p == git_bash, which=lambda n: None)
    assert found and found[0].argv[0] == git_bash


def test_linux_finds_bash():
    found = shells.detect("linux", exists=lambda p: False, which=lambda n: f"/usr/bin/{n}" if n == "bash" else None)
    assert found and found[0].argv[0] == "/usr/bin/bash"
