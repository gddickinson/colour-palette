# colour-palette -- Interface Map

## Project Structure

```
colour-palette/
  colour_palette/          # Main package
    __init__.py            # Package init, re-exports Color, HarmonyType, ColorPaletteGenerator
    color.py               # Color dataclass (HSV with RGB/hex conversion), HarmonyType enum
    generator.py           # ColorPaletteGenerator class (harmony algorithms, palette analysis)
    visualizer.py          # visualize_palette() - PNG swatch output with gradient blends
    cli.py                 # CLI entry point (argparse), generate_and_save_palettes()
  _archive/
    colour-palette.py      # Original single-file version (archived)
  test_colour_palette.py   # Unit tests for Color and ColorPaletteGenerator
  requirements.txt         # numpy, matplotlib
  ROADMAP.md
  INTERFACE.md             # This file
  README.md
```

## Key Classes and Functions

| Symbol | File | Purpose |
|---|---|---|
| `Color` | `colour_palette/color.py` | HSV color dataclass with to_rgb(), to_hex(), from_rgb(), input validation |
| `HarmonyType` | `colour_palette/color.py` | Enum: complementary, triadic, analogous, split_complementary, tetradic, monochromatic |
| `ColorPaletteGenerator` | `colour_palette/generator.py` | Core logic: generate_base_color(), generate_harmony(), analyze_palette(), generate_palette() |
| `visualize_palette()` | `colour_palette/visualizer.py` | Creates PNG swatch image with color info and gradient blend |
| `main()` | `colour_palette/cli.py` | CLI entry point with --seed, --harmony, --colors, --output-dir |

## Module Connections

- `cli.py` imports from `color.py`, `generator.py`, `visualizer.py`
- `generator.py` imports from `color.py`
- `visualizer.py` imports from `color.py`
- Tests import from `colour_palette.color` and `colour_palette.generator`
