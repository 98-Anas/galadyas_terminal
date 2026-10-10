from mindas_terminal import shells


def test_windows_prefers_git_bash():
    git_bash = r"C:\Program Files\Git\bin\bash.exe"
    found = shells.detect("win32", exists=lambda p: p == git_bash, which=lambda n: None)
    assert found and found[0].argv[0] == git_bash


def test_linux_finds_bash():
    found = shells.detect("linux", exists=lambda p: False, which=lambda n: f"/usr/bin/{n}" if n == "bash" else None)
    assert found and found[0].argv[0] == "/usr/bin/bash"


def test_safe_which_ignores_current_folder(tmp_path, monkeypatch):
    import sys
    name = "fake-tool.exe" if sys.platform == "win32" else "fake-tool"
    planted = tmp_path / name
    planted.write_text("x")
    planted.chmod(0o755)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PATH", f".{__import__('os').pathsep}{tmp_path}")
    assert shells.safe_which("fake-tool") is None          # "." and the current folder are both refused
