"""Tests for the colour_palette package."""

import json
import os
import tempfile
import unittest

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


if __name__ == "__main__":
    unittest.main()
