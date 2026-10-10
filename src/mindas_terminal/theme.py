"""The space theme. Self-contained so the terminal has no dependency on the rest of mindas."""

from __future__ import annotations

NAME = "mindas-space"

COLORS = dict(
    primary="#7aa2ff",
    secondary="#b18cff",
    accent="#5eead4",
    foreground="#e6e9f5",
    background="#070b1a",
    surface="#0e1430",
    panel="#141b3d",
    success="#4ade80",
    warning="#fbbf24",
    error="#f87171",
)


def apply(app) -> None:
    """Register and select the theme on a Textual App (call from on_mount)."""
    from textual.theme import Theme

    app.register_theme(Theme(name=NAME, dark=True, **COLORS))
    app.theme = NAME
