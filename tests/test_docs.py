import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import gen_docs  # noqa: E402


def test_reference_pages_match_the_code():
    assert gen_docs.main(check=True) == 0, "run: uv run python tools/gen_docs.py"


def test_wiki_links_point_to_existing_pages():
    import re

    docs = Path(gen_docs.DOCS)
    pages = {p.stem for p in docs.glob("*.md")}
    for page in docs.glob("*.md"):
        for target in re.findall(r"\]\(([A-Za-z-]+)(?:#[^)]*)?\)", page.read_text(encoding="utf-8")):
            assert target in pages, f"{page.name} links to missing page {target}"


def test_man_page_is_valid_roff_shape():
    from galadyas_terminal import manpage

    page = manpage.render()
    assert page.startswith(".TH GALADYAS")
    for section in ("NAME", "SYNOPSIS", "DESCRIPTION", "OPTIONS", "KEYS", "FILES", "SECURITY", "SEE ALSO"):
        assert f".SH {section}" in page
    assert all(not line.startswith("'") for line in page.splitlines())
