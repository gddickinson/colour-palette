"""ColorPaletteGenerator - generates harmonious color palettes using color theory."""

import random
from typing import Dict, List

import numpy as np

from colour_palette.color import Color, HarmonyType


class ColorPaletteGenerator:
    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        self.color_meanings = {
            "red": "energy, passion, excitement",
            "blue": "trust, peace, stability",
            "green": "growth, harmony, freshness",
            "yellow": "happiness, optimism, creativity",
            "purple": "royalty, luxury, mystery",
            "orange": "enthusiasm, adventure, confidence",
        }

    def generate_base_color(self, temperature: str = "neutral") -> Color:
        """Generate a base color with given temperature preference.

        Args:
            temperature: One of 'warm', 'cool', or 'neutral'.
        """
        if temperature == "warm":
            # Red-to-yellow range; wraps around hue circle
            h = random.uniform(0.95, 1.15) % 1.0
        elif temperature == "cool":
            h = random.uniform(0.45, 0.65)
        else:
            h = random.random()

        s = random.uniform(0.6, 0.9)
        v = random.uniform(0.7, 0.9)
        return Color(h, s, v)

    def adjust_color(
        self,
        color: Color,
        hue_shift: float = 0.0,
        sat_adjust: float = 0.0,
        val_adjust: float = 0.0,
    ) -> Color:
        """Return a new Color with adjusted HSV values."""
        new_h = (color.h + hue_shift) % 1.0
        new_s = float(np.clip(color.s + sat_adjust, 0, 1))
        new_v = float(np.clip(color.v + val_adjust, 0, 1))
        return Color(new_h, new_s, new_v)

    def generate_harmony(
        self,
        base_color: Color,
        harmony_type: HarmonyType,
        num_colors: int = 5,
    ) -> List[Color]:
        """Generate a color harmony based on the specified type."""
        colors = [base_color]

        if harmony_type == HarmonyType.COMPLEMENTARY:
            colors.append(self.adjust_color(base_color, hue_shift=0.5))

        elif harmony_type == HarmonyType.TRIADIC:
            colors.extend([
                self.adjust_color(base_color, hue_shift=1 / 3),
                self.adjust_color(base_color, hue_shift=2 / 3),
            ])

        elif harmony_type == HarmonyType.ANALOGOUS:
            for i in range(1, num_colors):
                shift = 0.05 * i
                colors.append(self.adjust_color(base_color, hue_shift=shift))

        elif harmony_type == HarmonyType.SPLIT_COMPLEMENTARY:
            complement = (base_color.h + 0.5) % 1.0
            colors.extend([
                Color(complement - 0.05, base_color.s, base_color.v),
                Color(complement + 0.05, base_color.s, base_color.v),
            ])

        elif harmony_type == HarmonyType.TETRADIC:
            colors.extend([
                self.adjust_color(base_color, hue_shift=0.25),
                self.adjust_color(base_color, hue_shift=0.5),
                self.adjust_color(base_color, hue_shift=0.75),
            ])

        elif harmony_type == HarmonyType.MONOCHROMATIC:
            for i in range(1, num_colors):
                sat_adjust = -0.15 * i
                val_adjust = 0.1 * i
                colors.append(
                    self.adjust_color(base_color, sat_adjust=sat_adjust, val_adjust=val_adjust)
                )

        return colors[:num_colors]

    def analyze_palette(self, colors: List[Color]) -> Dict:
        """Analyze the characteristics of a color palette.

        Returns dict with brightness (average), temperature ('warm'/'cool'),
        contrast (max-min brightness), and harmony_level (simple metric).
        """
        rgb_colors = [c.to_rgb() for c in colors]

        brightness = float(np.mean([sum(rgb) / 3 for rgb in rgb_colors]))
        warmth = float(np.mean([rgb[0] - rgb[2] for rgb in rgb_colors]))
        brightnesses = [sum(rgb) / 3 for rgb in rgb_colors]
        contrast = max(brightnesses) - min(brightnesses)

        return {
            "brightness": brightness,
            "temperature": "warm" if warmth > 0 else "cool",
            "contrast": contrast,
            "harmony_level": min(1.0, contrast * 2),
        }

    def generate_palette(
        self,
        temperature: str = "neutral",
        harmony_type: HarmonyType = HarmonyType.COMPLEMENTARY,
        num_colors: int = 5,
    ) -> Dict:
        """Generate a complete color palette with analysis."""
        base_color = self.generate_base_color(temperature)
        colors = self.generate_harmony(base_color, harmony_type, num_colors)
        analysis = self.analyze_palette(colors)

        palette_data = {
            "colors": [color.to_hex() for color in colors],
            "rgb_values": [tuple(int(x * 255) for x in color.to_rgb()) for color in colors],
            "hsv_values": [(color.h, color.s, color.v) for color in colors],
            "analysis": analysis,
            "harmony_type": harmony_type.value,
            "temperature": temperature,
        }
        return palette_data
