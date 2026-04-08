# Color Palette Generator -- Roadmap

## Current State
A single-file Python tool (`colour-palette.py`) generating harmonious color palettes using color theory. Implements 6 harmony types (complementary, triadic, analogous, split-complementary, tetradic, monochromatic) with a `Color` dataclass and `ColorPaletteGenerator` class. Outputs PNG visualizations and JSON data. Uses dataclasses, enums, and type hints. Clean code with proper structure, but everything in one file.

## Short-term Improvements
- [x] Add `requirements.txt` (numpy, matplotlib)
- [x] Rename `colour-palette.py` to `colour_palette.py` for valid Python import
- [x] Split into modules: `color.py` (Color dataclass), `generator.py` (palette logic), `visualizer.py` (plotting), `cli.py` (main)
- [x] Add CLI arguments for seed, harmony type, number of colors, and output format
- [x] Add unit tests for harmony calculations (e.g., complementary should be 180 degrees apart)
- [x] Validate color inputs (HSV values in 0-1 range)

## Feature Enhancements
- [ ] Add WCAG contrast ratio checking for accessibility compliance
- [ ] Generate CSS/Tailwind/SASS color variable exports
- [ ] Add interactive mode using matplotlib widgets (pick base color, see harmonies live)
- [ ] Implement color blindness simulation (protanopia, deuteranopia, tritanopia)
- [ ] Add palette extraction from images (dominant color extraction via k-means)
- [ ] Support OKLCH and CIELAB color spaces for perceptually uniform palettes
- [ ] Generate gradient CSS code alongside palette swatches

## Long-term Vision
- [ ] Build a web UI for interactive palette creation (Flask + Canvas)
- [ ] Add AI-powered palette suggestions based on mood/theme keywords
- [ ] Create a Figma/Sketch plugin that exports palettes directly
- [ ] Support design system generation (primary, secondary, accent, semantic colors)
- [ ] Add palette history and favorites with local storage

## Technical Debt
- [x] Generated PNG files (`palette_*.png`) and `palette_data.json` are in the repo -- add `.gitignore`
- [x] Hyphenated filename prevents Python import -- rename immediately
- [x] No `__main__.py` or entry point -- add proper CLI with argparse
- [ ] Temperature control logic in `generate_palette()` may not cover edge cases -- add tests
- [ ] Color analysis metrics (brightness, contrast, harmony) lack documentation of formulas
