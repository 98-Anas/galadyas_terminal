"""Themes: space (default, dark), light, and high contrast for accessibility. Self-contained."""

from __future__ import annotations

PALETTES = {
    "space": dict(dark=True, primary="#7aa2ff", secondary="#b18cff", accent="#5eead4", foreground="#e6e9f5",
                  background="#070b1a", surface="#0e1430", panel="#141b3d", success="#4ade80",
                  warning="#fbbf24", error="#f87171"),
    "light": dict(dark=False, primary="#2f5fd0", secondary="#7c4dcc", accent="#0f766e", foreground="#1b2033",
                  background="#f7f8fc", surface="#ffffff", panel="#e3e7f3", success="#15803d",
                  warning="#b45309", error="#b91c1c"),
    "contrast": dict(dark=True, primary="#ffffff", secondary="#ffff00", accent="#00ffff", foreground="#ffffff",
                     background="#000000", surface="#000000", panel="#1a1a1a", success="#00ff00",
                     warning="#ffff00", error="#ff5555"),
}
COLORS = PALETTES["space"]
NAME = "mindas-space"


def apply(app, name: str = "space") -> None:
    """Register every palette and select one on a Textual App."""
    from textual.theme import Theme

    for key, palette in PALETTES.items():
        if f"mindas-{key}" not in app.available_themes:
            app.register_theme(Theme(name=f"mindas-{key}", **palette))
    app.theme = f"mindas-{name if name in PALETTES else 'space'}"
