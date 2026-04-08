"""Command-line interface for the colour-palette generator."""

import argparse
import json
import os

from colour_palette.color import Color, HarmonyType
from colour_palette.generator import ColorPaletteGenerator
from colour_palette.visualizer import visualize_palette


def generate_and_save_palettes(
    seed: int = None,
    output_dir: str = ".",
    harmony_type: str = None,
    num_colors: int = 5,
):
    """Generate palettes and save PNGs + JSON data.

    Args:
        seed: Random seed for reproducibility.
        output_dir: Directory to write output files.
        harmony_type: If given, generate only this harmony; otherwise all.
        num_colors: Number of colors per palette.
    """
    generator = ColorPaletteGenerator(seed)
    os.makedirs(output_dir, exist_ok=True)

    if harmony_type:
        harmonies = [HarmonyType(harmony_type)]
    else:
        harmonies = list(HarmonyType)

    all_palettes = {}
    for harmony in harmonies:
        print(f"\nGenerating {harmony.value} palette...")

        palette_data = generator.generate_palette(
            harmony_type=harmony,
            num_colors=num_colors,
        )

        colors = [
            Color.from_rgb(r / 255, g / 255, b / 255)
            for r, g, b in palette_data["rgb_values"]
        ]
        visualize_palette(
            colors,
            title=f"{harmony.value.title()} Color Harmony",
            filename=os.path.join(output_dir, f"palette_{harmony.value}.png"),
        )

        all_palettes[harmony.value] = palette_data

    json_path = os.path.join(output_dir, "palette_data.json")
    with open(json_path, "w") as f:
        json.dump(all_palettes, f, indent=2)

    print("\nGenerated palettes for all harmony types!")
    print(f"Check {output_dir} for PNG files and palette_data.json.")


def main():
    parser = argparse.ArgumentParser(
        description="Generate harmonious color palettes using color theory.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument(
        "--harmony",
        choices=[h.value for h in HarmonyType],
        default=None,
        help="Harmony type (default: all)",
    )
    parser.add_argument("--colors", type=int, default=5, help="Number of colors (default: 5)")
    parser.add_argument("--output-dir", default=".", help="Output directory (default: .)")

    args = parser.parse_args()
    generate_and_save_palettes(
        seed=args.seed,
        output_dir=args.output_dir,
        harmony_type=args.harmony,
        num_colors=args.colors,
    )


if __name__ == "__main__":
    main()
