from galadyas_terminal import config


def test_defaults_when_empty():
    s, w = config.parse("")
    assert s == config.Settings() and w == []


def test_values_and_bad_input_are_handled():
    s, w = config.parse('theme = "light"\nprofile = "security"\nscrollback = 500\nnope = 1\nprefix = 3\n')
    assert (s.theme, s.profile, s.scrollback, s.prefix) == ("light", "security", 500, "ctrl+b")
    assert any("nope" in x for x in w) and any("prefix" in x for x in w)


def test_invalid_choices_fall_back():
    s, w = config.parse('theme = "neon"\nalias_style = "x"\nscrollback = -5\n')
    assert (s.theme, s.alias_style, s.scrollback) == ("space", "linux", 10_000) and len(w) == 3


def test_broken_toml_is_not_fatal():
    s, w = config.parse("theme = ")
    assert s == config.Settings() and w


def test_round_trip_and_escaping(tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    original = config.Settings(shell='Git "Bash"', profile="hpc", confirm_multiline_paste=False)
    config.save(original)
    loaded, warnings = config.load()
    assert loaded == original and warnings == []


def test_settings_from_the_former_name_are_migrated(tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    legacy = tmp_path / "mindas-terminal"
    legacy.mkdir()
    (legacy / "config.toml").write_text('theme = "light"\n', encoding="utf-8")
    p = config.path()
    assert p == tmp_path / "galadyas-terminal" / "config.toml"
    assert p.read_text(encoding="utf-8") == 'theme = "light"\n'
    assert (legacy / "config.toml").exists()  # the original is left untouched


def test_fresh_install_uses_the_new_folder(tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    assert config.path() == tmp_path / "galadyas-terminal" / "config.toml"
    assert not (tmp_path / "mindas-terminal").exists()
