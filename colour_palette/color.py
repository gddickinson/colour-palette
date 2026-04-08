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

    def to_hex(self) -> str:
        """Convert to hex color code."""
        rgb = self.to_rgb()
        return f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}"

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
