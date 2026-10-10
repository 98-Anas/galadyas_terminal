from mindas_terminal.copymode import CopyMode

LINES = ["alpha beta", "gamma Delta", "", "error: disk full", "done"]


def cm():
    return CopyMode.at_bottom(list(LINES), height=3)


def test_starts_at_bottom_and_moves():
    c = cm()
    assert c.row == 4 and c.top == 2
    c.goto_top()
    assert (c.row, c.top) == (0, 0)
    c.move(rows=100)
    assert c.row == 4


def test_words():
    c = cm()
    c.goto_top()
    c.word_forward()
    assert (c.row, c.col) == (0, 6)
    c.word_forward()
    assert (c.row, c.col) == (1, 0)
    c.word_back()
    assert (c.row, c.col) == (0, 6)


def test_smartcase_search_and_next():
    c = cm()
    c.goto_top()
    assert c.search("delta")
    assert (c.row, c.col) == (1, 6)
    assert not c.search("delta-missing")
    c.search("Delta")
    assert c.matches == [(1, 6)]
    c.goto_top()
    c.search("a")
    assert (c.row, c.col) == (0, 4)               # the next match after the cursor
    c.next_match()
    assert (c.row, c.col) == (0, 9)
    c.next_match(forward=False)
    assert (c.row, c.col) == (0, 4)


def test_selection_and_yank():
    c = cm()
    c.goto_top()
    c.toggle_select()
    c.word_forward()
    c.move(cols=3)
    assert c.selected_text() == "alpha beta"
    c.toggle_select(linewise=True)
    c.move(rows=1)
    assert c.selected_text() == "alpha beta\ngamma Delta"
