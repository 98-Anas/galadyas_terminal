# Contributing

Thank you for helping. Bug reports, documentation fixes, new toolkit commands and code are all welcome.

## Set up

```bash
git clone https://github.com/98-Anas/galadyas_terminal && cd galadyas_terminal
uv sync
uv run pytest
```

Tests start real shells: on Windows, Git Bash is used when installed; on Linux, bash.

## Before you open a pull request

1. `uv run python tools/ci.py` passes (tests, docs, lint, dependency audit). Add `--full` if you touched the
   terminal widget, screen or PTY code, and `--linux` on Windows to run everything on Linux through WSL too.
2. There is no hosted CI: the local CI result is part of the pull request description.
3. If you changed toolkits or aliases: `uv run python tools/gen_docs.py`, and commit the regenerated pages.
4. New behaviour has a test. Pure logic goes in a pure module with plain tests (see
   [Architecture](docs/Architecture.md)).
5. User-visible changes are described in [CHANGELOG.md](CHANGELOG.md) and in the docs.
6. Screenshots come only from `uv run python tools/screenshots.py`: it uses a demo environment and refuses to
   write an image that contains your user name, host name or home folder. Never commit screenshots of your
   own machine.

## Adding toolkit commands

Edit `src/galadyas_terminal/toolkit.py`:

```python
T("devops", "Restart a deployment", "kubectl rollout restart deployment/<name> -n <namespace>"),
```

- The title says what it does, in plain words, starting with the outcome.
- Use `<snake_case>` placeholders for values the user must supply.
- Set the platform (`linux` or `windows`) when the command works on only one.
- Prefer read-only or reversible commands. Destructive commands need a note explaining the effect.
- Security commands must serve defence or authorised testing and carry `SECURITY_NOTICE` when they scan or
  probe.

## Style

- Python 3.11+, type hints, small functions, comments only where the reason is not obvious.
- No new runtime dependency without discussion: each one is a supply-chain risk.
- Docs in plain, direct English; no emojis.

## Code of conduct

Be respectful and constructive. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## License

By contributing, you agree that your contributions are licensed under the Apache License 2.0.
