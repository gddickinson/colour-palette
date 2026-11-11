# colour-palette -- Interface Map

## Project Structure

```
colour-palette/
  colour_palette/          # Main package
    __init__.py            # Package init, re-exports Color, HarmonyType, ColorPaletteGenerator
    color.py               # Color dataclass (HSV with RGB/hex conversion), HarmonyType enum
    generator.py           # ColorPaletteGenerator (harmony algorithms, analysis), generate_palettes() (one CLI run)
    visualizer.py          # visualize_palette() PNG swatches; gradient_blend() strip
    cli.py                 # CLI entry point (argparse), generate_and_save_palettes()
    web/                   # Web interface (FastAPI) + static GitHub Pages site
      __init__.py
      app.py               # routes under /api, STATIC_ENDPOINTS exported by scripts/build_static.py
      static/              # plain ES-module front end, no build step
        index.html, style.css (shared kit theme), style_app.css (accents + page styles), icon.svg
        core.js            # kit: api(), hash router, helpers (unchanged copy)
        main.js            # registers pages, footer mode text
        static_api.js      # answers api() on the static site (exported JSON + colour_engine.js)
        colour_engine.js   # JS port: PyRandom (MT19937 + CPython seeding), colorsys, Color, PaletteGenerator,
                           #   generatePalettes, gradientBlend
        colour_engine.test.mjs  # node test against tests/fixtures/colour_engine.json
        ui.js              # swatch cards, copy buttons, analysis, gradient canvas, JSON/CSS/PNG export
        home.js, generate.js, harmonies.js, check.js, about.js   # one module per page
  scripts/
    build_static.py        # export the static site to site/
    screenshots.py         # Playwright smoke test + README images (docs/img/)
    make_engine_fixture.py # Python reference values for the JS engine test
  tests/
    test_web.py            # API, static build, fixture-is-current, node engine test
    fixtures/colour_engine.json
  test_colour_palette.py   # Unit + regression tests for the package
  colour_palette.py        # Entry-point wrapper -> cli.main()
  run_web.py               # start the web app on 127.0.0.1:8150
  requirements.txt         # numpy, matplotlib
  requirements-web.txt     # pinned web/test dependencies
  .github/workflows/pages.yml  # tests + publish site/ to GitHub Pages on push to main
  _archive/colour-palette.py   # Original single-file version (archived)
  palette_*.png, palette_data.json  # output of the default CLI run (seed 42)
  ROADMAP.md, SESSION_LOG.md, INTERFACE.md, README.md
```

## Key Classes and Functions

| Symbol | File | Purpose |
|---|---|---|
| `Color` | `colour_palette/color.py` | HSV color dataclass with to_rgb(), to_hex(), from_rgb(), input validation |
| `HarmonyType` | `colour_palette/color.py` | Enum: complementary, triadic, analogous, split_complementary, tetradic, monochromatic |
| `ColorPaletteGenerator` | `colour_palette/generator.py` | generate_base_color(), generate_harmony(), analyze_palette(), generate_palette(), palette_from_base() |
| `generate_palettes()` | `colour_palette/generator.py` | One CLI run: {harmony: palette dict} from one seeded generator |
| `visualize_palette()` / `gradient_blend()` | `colour_palette/visualizer.py` | PNG swatch image / the gradient strip array |
| `main()` | `colour_palette/cli.py` | CLI entry point with --seed, --harmony, --colors, --output-dir |
| `app`, `STATIC_ENDPOINTS` | `colour_palette/web/app.py` | /api/info, /api/palette, /api/cli/{seed}, /api/palette_data, /api/png |

## Module Connections

- `cli.py` imports from `color.py`, `generator.py`, `visualizer.py`
- `generator.py` imports from `color.py`; `visualizer.py` imports from `color.py`
- `web/app.py` imports `color.py`, `generator.py` (and `visualizer.py` lazily for /api/png)
- `web/static/colour_engine.js` mirrors `color.py` + `generator.py` + `gradient_blend`; tested against
  `scripts/make_engine_fixture.py` output
- Tests import from `colour_palette.color`, `colour_palette.generator`, `colour_palette.visualizer`, `colour_palette.cli`
