# Claude collaboration notes for `colour-palette`

This project was built with substantial assistance from **Claude (Anthropic)**, primarily via **Claude Code**.

## Global preferences

George's global Claude preferences live in `~/.claude/CLAUDE.md` and apply to every project. Highlights:

- Keep all source files under 500 lines; split into focused modules if approaching that limit.
- For Python projects, maintain an `INTERFACE.md` at the project root as a navigation map of modules, classes, and key functions.
- Prefer many small, focused files over fewer large ones.
- Group related functionality; extract reusable logic into utility modules.

## Project navigation

See [`INTERFACE.md`](./INTERFACE.md) for a navigation map of this repository's modules and how they connect. Read `INTERFACE.md` before opening individual source files.

## Working with Claude on this repo

When directing Claude Code on this codebase, follow the global rules above, prefer making targeted edits via the `Edit` tool over rewriting whole files, and update `INTERFACE.md` whenever the project structure changes.

Project-specific conventions, build instructions, and lab-specific notes should be added below as the project evolves.

@INTERFACE.md

## Web interface

- `python run_web.py` (port 8150); tests: `python -m pytest -q tests/test_web.py test_colour_palette.py`.
- `colour_palette/web/static/colour_engine.js` must stay in step with `color.py` / `generator.py`: after changing the
  Python, run `python scripts/make_engine_fixture.py --write` and `node colour_palette/web/static/colour_engine.test.mjs`
  (test_web.py fails if the fixture is stale).
