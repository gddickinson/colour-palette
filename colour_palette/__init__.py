"""
colour_palette - Harmonious color palette generator using color theory.

Submodules:
    color      - Color dataclass and HarmonyType enum
    generator  - ColorPaletteGenerator class with harmony algorithms
    visualizer - Palette visualization and PNG output
    cli        - Command-line interface and entry point
"""

from colour_palette.color import Color, HarmonyType
from colour_palette.generator import ColorPaletteGenerator

__all__ = ["Color", "HarmonyType", "ColorPaletteGenerator"]
