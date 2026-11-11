"""Color dataclass and HarmonyType enum for color palette generation."""

import colorsys
from dataclasses import dataclass
from enum import Enum
from typing import Tuple


class HarmonyType(Enum):
    COMPLEMENTARY = "complementary"
    TRIADIC = "triadic"
    ANALOGOUS = "analogous"
    SPLIT_COMPLEMENTARY = "split_complementary"
    TETRADIC = "tetradic"
    MONOCHROMATIC = "monochromatic"


@dataclass
class Color:
    h: float  # Hue (0-1)
    s: float  # Saturation (0-1)
    v: float  # Value/Brightness (0-1)

    def to_rgb(self) -> Tuple[float, float, float]:
        """Convert HSV to RGB (each channel 0-1)."""
        return colorsys.hsv_to_rgb(self.h, self.s, self.v)

    def to_rgb255(self) -> Tuple[int, int, int]:
        """RGB as integers 0-255, rounded to nearest (so hex -> Color -> hex round-trips)."""
        r, g, b = self.to_rgb()
        return round(r * 255), round(g * 255), round(b * 255)

    def to_hex(self) -> str:
        """Convert to hex color code."""
        return "#%02x%02x%02x" % self.to_rgb255()

    @classmethod
    def from_rgb(cls, r: float, g: float, b: float) -> 'Color':
        """Create Color from RGB values (each channel 0-1)."""
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        return cls(h, s, v)

    def __post_init__(self):
        """Validate that HSV values are in 0-1 range."""
        # Wrap hue to 0-1 range
        self.h = self.h % 1.0
        # Clamp saturation and value
        self.s = max(0.0, min(1.0, self.s))
        self.v = max(0.0, min(1.0, self.v))
