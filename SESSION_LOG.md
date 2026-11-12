# Session log

## 2026-11-11 — web interface and static GitHub Pages site (branch `web-interface`)

Added a FastAPI web app (`colour_palette/web/`, `run_web.py`, port 8150) and a static site built by
`scripts/build_static.py` and published by `.github/workflows/pages.yml`. Pages: home, generator, harmonies,
cross-check, about. The static site is the full generator: `colour_engine.js` ports `color.py`, `generator.py` and
`gradient_blend`, plus CPython's Mersenne Twister seeding, `colorsys`, NumPy's pairwise mean and Python 3.12's
compensated `sum()`, so every number matches the Python bit for bit (node test: 475 checks, 6,159 floats, all
identical; live check of random seeds up to 2^40 on the local app also matches).

Refactor (no behaviour change): `generate_palettes()` and `ColorPaletteGenerator.palette_from_base()` factored out of
the CLI for the web API.

Bugs fixed in the existing code (each in its own commit, with a regression test in `test_colour_palette.py`):
- `--colors 0` crashed in `analyze_palette` (max() of empty list): now a clear ValueError / argparse error.
- The PNG gradient strip left black columns (whole strip for one colour; the tail for 4, 6, 7, 8 ... colours).
- PNG labels (RGB/hex) were often one level lower than `palette_data.json`, because the CLI rebuilt colours from the
  truncated 0-255 RGB; committed `palette_*.png` regenerated (5 of 6 had wrong labels).
- Seeds below 0 or above 2^32 - 1 crashed in `np.random.seed`.
- README: wrong script/module names, `visualize_palette` called as a method, "contrast ratio" wording.

George approved rounding (2026-11-11). `Color.to_hex` and `rgb_values` truncated with `int(x * 255)`, so a picked
#12ab34 came back as #11ab34. They now round (new `Color.to_rgb255()`, used by to_hex, generate_palette and the PNG
labels; JS `rgb255` uses a ties-to-even `pyRound` like Python's `round`). Every 24-bit colour now round-trips (node test
checks all 16.7M; Python test a dense ~300k sample). Committed `palette_data.json` and `palette_*.png` regenerated
(seed 42: 19 of 22 hex codes move up by one level), engine fixture rewritten, web truncation note removed.

Removed the root `colour-palette.py` (an identical copy of `_archive/colour-palette.py`, still truncating hex values; nothing referenced it). ROADMAP's "Current State" now says the single file is archived.
