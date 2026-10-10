import asyncio

import pytest

from mindas_terminal import shells
from mindas_terminal.app import MindasTerminal
from mindas_terminal.widget import TerminalPane

SHELL = shells.detect()[0]
pytestmark = pytest.mark.skipif(not SHELL, reason="no shell")


async def wait(pane, needle, timeout=20):
    for _ in range(int(timeout / 0.05)):
        if needle in "\n".join(pane.screen_model.display):
            return
        await asyncio.sleep(0.05)
    raise AssertionError(f"{needle!r} not on screen")


async def test_tabs_splits_prefix_and_copy_mode():
    app = MindasTerminal(SHELL)
    async with app.run_test(size=(120, 36)) as pilot:
        await asyncio.sleep(1.5)
        assert len(app.all_panes()) == 1
        await pilot.press("ctrl+b", "percent_sign")          # split right
        await asyncio.sleep(0.3)
        await pilot.press("ctrl+b", "quotation_mark")        # split down
        await asyncio.sleep(0.3)
        assert len(app.all_panes()) == 3
        await pilot.press("ctrl+b", "z")
        assert app._zoomed is not None
        await pilot.press("ctrl+b", "z")
        assert app._zoomed is None
        await pilot.press("ctrl+b", "c")                     # new tab
        await asyncio.sleep(0.5)
        assert len(app._tab_ids()) == 2
        await pilot.press("ctrl+b", "1")
        assert app.tabbed.active == app._tab_ids()[0]

        pane = app.current_pane()
        echo = "Write-Output" if "PowerShell" in SHELL.name or SHELL.name == "cmd" else "echo"
        pane.write(f"{echo} FIND-ME-{'4' + '2'}\r")
        await wait(pane, "FIND-ME-42")
        await pilot.press("ctrl+b", "left_square_bracket")   # copy mode
        assert pane.copy is not None
        await pilot.press("question_mark", *"find-me-42", "enter", "V", "y")
        assert pane.copy is None
        assert "FIND-ME-42" in app.paste_buffer


async def test_multiline_paste_asks_first():
    app = MindasTerminal(SHELL)
    async with app.run_test(size=(100, 30)) as pilot:
        await asyncio.sleep(1.0)
        pane = app.current_pane()
        from mindas_terminal.screen import BRACKETED_PASTE
        sent = []
        pane.write = sent.append
        pane.screen_model.mode.add(BRACKETED_PASTE)          # the shell protects pastes: wrapped, no question
        pane.paste_text("echo one\necho two")
        await pilot.pause()
        assert sent == ["\x1b[200~echo one\recho two\x1b[201~"]
        pane.screen_model.mode.discard(BRACKETED_PASTE)      # unprotected: the lines would run, so ask
        pane.paste_text("echo one\necho two")
        await pilot.pause()
        assert type(app.screen).__name__ == "Confirm"
        await pilot.press("n")
        assert type(app.screen).__name__ != "Confirm"


async def test_task_manager_opens_and_lists():
    app = MindasTerminal(SHELL)
    async with app.run_test(size=(140, 40)) as pilot:
        await asyncio.sleep(1.0)
        await pilot.press("ctrl+b", "t")
        from textual.widgets import DataTable
        for _ in range(100):                                 # first collection can take a few seconds
            await asyncio.sleep(0.1)
            if app.screen.query_one(DataTable).row_count > 5:
                break
        assert app.screen.query_one(DataTable).row_count > 5
        await pilot.press("f")                               # only this terminal's processes
        await pilot.pause()
        await pilot.press("q")
        assert isinstance(app.focused, TerminalPane) or app.screen is app.screen_stack[0]


async def test_toolkit_inserts_without_running():
    app = MindasTerminal(SHELL, profile="network")
    async with app.run_test(size=(140, 40)) as pilot:
        await asyncio.sleep(1.0)
        pane = app.current_pane()
        sent = []
        pane.write = sent.append                              # capture what would reach the shell
        await pilot.press("ctrl+b", "g")
        await pilot.pause()
        await pilot.press(*"http headers", "enter")           # needs a <url>
        await pilot.pause()
        await pilot.press(*"example.com", "enter")
        await pilot.pause()
        assert sent == ["curl -sSI example.com"]              # inserted; no Enter, so it does not run
