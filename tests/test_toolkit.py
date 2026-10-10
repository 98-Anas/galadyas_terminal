from mindas_terminal import aliases, toolkit


def test_every_field_has_commands_on_both_platforms():
    for platform in ("win32", "linux"):
        tools = toolkit.for_platform(platform)
        expected = set(toolkit.FIELDS) - ({"windows"} if platform == "linux" else set())
        assert {t.field for t in tools} == expected
    assert len(toolkit.TOOLS) >= 100


def test_search_all_words_and_profile_first():
    tools = toolkit.for_platform("linux")
    hits = toolkit.search(tools, "slurm gpu")
    assert hits and all(t.field == "hpc" for t in hits)
    assert toolkit.search(tools, "", profile="security")[0].field == "security"


def test_quote_keeps_one_argument_and_blocks_injection():
    assert toolkit.quote("example.com") == "example.com"
    assert toolkit.quote("a b") == "'a b'"
    q = toolkit.quote("x'; rm -rf ~ #\n")
    assert q.startswith("'") and q.endswith("'") and q.count("'") == 2 and "\n" not in q


def test_security_tools_carry_the_ethics_notice():
    scans = [t for t in toolkit.TOOLS if "nmap" in t.command]
    assert scans and all(t.note == toolkit.SECURITY_NOTICE for t in scans)


def test_aliases_unique_and_documented():
    names = [a.name for a in aliases.ALIASES]
    assert len(names) == len(set(names)) and len(names) >= 60
    assert all(a.help and a.group in aliases.GROUPS for a in aliases.ALIASES)
    assert "malias()" in aliases.bash() and "function mkcd" in aliases.powershell()
