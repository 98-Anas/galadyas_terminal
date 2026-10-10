#!/usr/bin/env bash
# Local CI on Linux (called by tools/ci.py --linux through WSL, or run directly on a Linux machine).
# Copies the project to the Linux file system so the virtual environment is a real Linux one.
set -euo pipefail
SRC="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="$HOME/.local/bin:$PATH"
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh -s -- -q
export PATH="$HOME/.local/bin:$PATH"
WORK="$HOME/.mindas-terminal-ci"
rm -rf "$WORK" && mkdir -p "$WORK"
(cd "$SRC" && tar --exclude=.venv --exclude=.git -cf - .) | tar -xf - -C "$WORK"
cd "$WORK"
uv sync -q --locked
uv run python tools/ci.py --no-audit "$@"
