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
