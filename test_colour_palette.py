"""Tests for the colour_palette package."""

import json
import os
import tempfile
import unittest

import numpy as np

from colour_palette.color import Color, HarmonyType
from colour_palette.generator import ColorPaletteGenerator


class TestColor(unittest.TestCase):
    """Tests for the Color dataclass."""

    def test_to_rgb_pure_red(self):
        c = Color(0.0, 1.0, 1.0)
        r, g, b = c.to_rgb()
        self.assertAlmostEqual(r, 1.0)
        self.assertAlmostEqual(g, 0.0)
        self.assertAlmostEqual(b, 0.0)

    def test_to_hex(self):
        c = Color(0.0, 1.0, 1.0)  # Pure red
        self.assertEqual(c.to_hex(), "#ff0000")

    def test_from_rgb_roundtrip(self):
        original = Color(0.3, 0.8, 0.9)
        rgb = original.to_rgb()
        restored = Color.from_rgb(*rgb)
        self.assertAlmostEqual(original.h, restored.h, places=5)
        self.assertAlmostEqual(original.s, restored.s, places=5)
        self.assertAlmostEqual(original.v, restored.v, places=5)

    def test_validation_clamps_saturation(self):
        c = Color(0.5, 1.5, -0.1)
        self.assertEqual(c.s, 1.0)
        self.assertEqual(c.v, 0.0)

    def test_validation_wraps_hue(self):
        c = Color(1.3, 0.5, 0.5)
        self.assertAlmostEqual(c.h, 0.3, places=5)


class TestColorPaletteGenerator(unittest.TestCase):
    """Tests for the ColorPaletteGenerator class."""

    def setUp(self):
        self.gen = ColorPaletteGenerator(seed=42)

    def test_complementary_is_180_degrees(self):
        base = Color(0.25, 0.8, 0.9)
        colors = self.gen.generate_harmony(base, HarmonyType.COMPLEMENTARY)
        complement = colors[1]
        diff = abs(complement.h - base.h)
        self.assertAlmostEqual(diff, 0.5, places=5)

    def test_triadic_is_120_degrees(self):
        base = Color(0.1, 0.8, 0.9)
        colors = self.gen.generate_harmony(base, HarmonyType.TRIADIC)
        self.assertEqual(len(colors), 3)
        diff1 = (colors[1].h - base.h) % 1.0
        diff2 = (colors[2].h - base.h) % 1.0
        self.assertAlmostEqual(diff1, 1 / 3, places=5)
        self.assertAlmostEqual(diff2, 2 / 3, places=5)

    def test_tetradic_produces_4_colors(self):
        base = Color(0.0, 0.8, 0.8)
        colors = self.gen.generate_harmony(base, HarmonyType.TETRADIC)
        self.assertEqual(len(colors), 4)

    def test_analogous_respects_num_colors(self):
        base = Color(0.5, 0.8, 0.8)
        colors = self.gen.generate_harmony(base, HarmonyType.ANALOGOUS, num_colors=7)
        self.assertEqual(len(colors), 7)

    def test_monochromatic_same_hue(self):
        base = Color(0.6, 0.9, 0.9)
        colors = self.gen.generate_harmony(base, HarmonyType.MONOCHROMATIC, num_colors=4)
        for c in colors:
            self.assertAlmostEqual(c.h, base.h, places=5)

    def test_generate_palette_returns_expected_keys(self):
        palette = self.gen.generate_palette()
        for key in ("colors", "rgb_values", "hsv_values", "analysis", "harmony_type", "temperature"):
            self.assertIn(key, palette)

    def test_analyze_palette_keys(self):
        colors = [Color(0.0, 0.8, 0.9), Color(0.5, 0.8, 0.9)]
        analysis = self.gen.analyze_palette(colors)
        for key in ("brightness", "temperature", "contrast", "harmony_level"):
            self.assertIn(key, analysis)

    def test_warm_temperature_generates_warm_hues(self):
        """Warm colors should be in the red-yellow range (hue near 0 or near 1)."""
        gen = ColorPaletteGenerator(seed=123)
        for _ in range(10):
            c = gen.generate_base_color("warm")
            # Warm hues: 0.95-1.0 or 0.0-0.15
            self.assertTrue(c.h >= 0.85 or c.h <= 0.25,
                            f"Warm hue {c.h} out of expected range")

    def test_seed_reproducibility(self):
        gen1 = ColorPaletteGenerator(seed=99)
        p1 = gen1.generate_palette()
        gen2 = ColorPaletteGenerator(seed=99)
        p2 = gen2.generate_palette()
        self.assertEqual(p1["colors"], p2["colors"])


class TestRegressions(unittest.TestCase):
    """Regression tests for bugs fixed in Nov 2026."""

    def test_zero_colors_rejected_clearly(self):
        gen = ColorPaletteGenerator(seed=1)
        with self.assertRaises(ValueError):
            gen.generate_harmony(Color(0.1, 0.8, 0.8), HarmonyType.TRIADIC, num_colors=0)

    def test_cli_rejects_zero_colors(self):
        import sys
        from colour_palette import cli
        old = sys.argv
        sys.argv = ["colour_palette.py", "--colors", "0", "--output-dir", tempfile.mkdtemp()]
        try:
            with self.assertRaises(SystemExit):
                cli.main()
        finally:
            sys.argv = old

    def test_gradient_has_no_black_gaps(self):
        """The blend strip left unfilled (black) columns: all of it for one colour, the tail for 4, 6, 7, 8 colours."""
        from colour_palette.visualizer import gradient_blend
        for n in range(1, 9):
            colors = [Color(i / 9, 0.8, 0.9) for i in range(n)]
            g = gradient_blend(colors)
            self.assertEqual(g.shape, (2, 256, 3))
            self.assertTrue((g.sum(axis=2) > 0).all(), f"black columns with {n} colours")
            self.assertTrue(np.allclose(g[0, 0], colors[0].to_rgb()))
            self.assertTrue(np.allclose(g[0, -1], colors[-1].to_rgb()))

    def test_png_labels_match_json(self):
        """The CLI rebuilt PNG colours from the 0-255 RGB (then truncated), so about a third of labels were 1 lower than JSON."""
        from unittest import mock
        from colour_palette import cli
        for seed in range(12):
            seen = []
            with mock.patch.object(cli, "visualize_palette", lambda colors, **kw: seen.append(colors)):
                out = tempfile.mkdtemp()
                cli.generate_and_save_palettes(seed=seed, output_dir=out)
            with open(os.path.join(out, "palette_data.json")) as f:
                data = json.load(f)
            for colors, palette in zip(seen, data.values()):
                self.assertEqual([c.to_hex() for c in colors], palette["colors"], f"seed {seed}")
                self.assertEqual([list(c.to_rgb255()) for c in colors], palette["rgb_values"])

    def test_any_integer_seed_works(self):
        """Seeds outside 0..2**32-1 crashed in np.random.seed although only Python's random (any int) is used."""
        for seed in (-1, 2 ** 32, 5_000_000_000, 2 ** 53 - 1):
            p1 = ColorPaletteGenerator(seed).generate_palette()
            p2 = ColorPaletteGenerator(seed).generate_palette()
            self.assertEqual(p1["colors"], p2["colors"])

    def test_hex_round_trips(self):
        """to_hex truncated int(x * 255), so e.g. #12ab34 -> Color.from_rgb -> to_hex gave #11ab34. Dense sample:
        every value of each channel against a grid of the other two, plus 100k random colours (the node test of the
        bit-identical JS port, colour_engine.test.mjs, checks all 16.7M)."""
        import random as rnd
        grid = range(0, 256, 17)
        samples = [(v, a, b) for v in range(256) for a in grid for b in grid]
        samples += [(a, v, b) for v in range(256) for a in grid for b in grid]
        samples += [(a, b, v) for v in range(256) for a in grid for b in grid]
        r = rnd.Random(2026)
        samples += [(r.randrange(256), r.randrange(256), r.randrange(256)) for _ in range(100_000)]
        for rgb in samples:
            c = Color.from_rgb(*(x / 255 for x in rgb))
            want = "#%02x%02x%02x" % rgb
            if c.to_hex() != want or c.to_rgb255() != rgb:
                self.fail(f"{want} came back as {c.to_hex()} / {c.to_rgb255()}")
        self.assertEqual(Color.from_rgb(0x12 / 255, 0xab / 255, 0x34 / 255).to_hex(), "#12ab34")


if __name__ == "__main__":
    unittest.main()
