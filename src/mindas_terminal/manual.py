"""The manual: the wiki pages, shipped inside the package, browsable and searchable offline.

Click a page on the left (or use Up/Down and Enter), click links inside a page to follow them, type in the
search box to find pages containing every word. Web links are copied, never opened automatically.
"""

from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Input, Markdown, OptionList, Static
from textual.widgets.option_list import Option

ORDER = ["Home", "Getting-Started", "Keyboard-Reference", "Field-Guides", "Tabs-and-Panes", "Copy-Mode",
         "Task-Manager", "Toolkits", "Aliases", "Configuration", "Security", "Troubleshooting", "FAQ",
         "Architecture", "Installation", "Toolkit-Reference", "Aliases-Reference"]


def docs_dir() -> Path:
    """Packaged copy first (installed app), then the repository's docs folder (development)."""
    for candidate in (Path(__file__).parent / "docs", Path(__file__).resolve().parents[2] / "docs"):
        if (candidate / "Home.md").is_file():
            return candidate
    return Path(__file__).parent / "docs"


def pages() -> list[str]:
    found = {p.stem for p in docs_dir().glob("*.md") if not p.stem.startswith("_")}
    return [p for p in ORDER if p in found] + sorted(found - set(ORDER))


def read(page: str) -> str:
    try:
        text = (docs_dir() / f"{page}.md").read_text(encoding="utf-8")
    except OSError:
        return f"# {page}\n\nThis page is not available in this installation."
    # Images do not render in a terminal; keep their caption.
    import re

    return re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"*[image: \1]*", text)


def search(query: str) -> list[str]:
    words = query.lower().split()
    if not words:
        return pages()
    return [p for p in pages() if all(w in (p.replace("-", " ") + " " + read(p)).lower() for w in words)]


def title(page: str) -> str:
    return page.replace("-", " ")


class ManualScreen(Screen[None]):
    DEFAULT_CSS = """
    ManualScreen { background: $background; }
    #man-head { height: 1; background: $panel; color: $accent; text-style: bold; padding: 0 1; }
    #man-side { width: 30; border-right: solid $panel; }
    #man-side Input { margin: 0; }
    #man-pages { height: 1fr; background: $background; border: none; }
    #man-body { width: 1fr; padding: 0 2; overflow-y: auto; }
    """
    BINDINGS = [
        Binding("escape,q", "close", "Close"),
        Binding("slash", "find", "Search"),
        Binding("b", "back", "Back"),
    ]

    def __init__(self, page: str = "Home") -> None:
        super().__init__()
        self.page = page
        self.history: list[str] = []

    def compose(self) -> ComposeResult:
        yield Static("mindas terminal manual   click a page or a link   / search   b back   Esc close", id="man-head")
        with Horizontal():
            with Vertical(id="man-side"):
                yield Input(placeholder="search the manual")
                yield OptionList(id="man-pages")
            with Vertical(id="man-body"):
                yield Markdown(id="man-doc", open_links=False)

    def on_mount(self) -> None:
        self._list(pages())
        self.show(self.page, remember=False)
        self.query_one(OptionList).focus()

    def _list(self, names: list[str]) -> None:
        ol = self.query_one(OptionList)
        ol.clear_options()
        for name in names:
            ol.add_option(Option(title(name), id=name))
        if names:
            ol.highlighted = 0

    def show(self, page: str, remember: bool = True) -> None:
        if remember and self.page != page:
            self.history.append(self.page)
        self.page = page
        ol = self.query_one(OptionList)
        for i in range(ol.option_count):
            if ol.get_option_at_index(i).id == page:
                ol.highlighted = i
                break
        self.query_one("#man-doc", Markdown).update(read(page))
        self.query_one("#man-body").scroll_home(animate=False)
        self.query_one("#man-head", Static).update(
            f"mindas terminal manual  >  {title(page)}   click a link to follow it   / search   b back   Esc close")

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        if event.option.id:
            self.show(event.option.id)

    def on_markdown_link_clicked(self, event: Markdown.LinkClicked) -> None:
        event.prevent_default()
        href = event.href
        if href.startswith(("http://", "https://")):
            self.app.copy_to_clipboard(href)
            self.notify(f"Link copied (not opened): {href}", timeout=4)
            return
        target = href.split("#", 1)[0].removesuffix(".md").split("/")[-1]
        if target in pages():
            self.show(target)

    def on_input_changed(self, event: Input.Changed) -> None:
        self._list(search(event.value))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        found = search(event.value)
        if found:
            self.show(found[0])
        self.query_one(OptionList).focus()

    def action_find(self) -> None:
        self.query_one(Input).focus()

    def action_back(self) -> None:
        if self.history:
            self.show(self.history.pop(), remember=False)

    def action_close(self) -> None:
        self.app.pop_screen()
