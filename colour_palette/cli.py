"""Command-line interface for the colour-palette generator."""

import argparse
import json
import os

from colour_palette.color import Color, HarmonyType
from colour_palette.generator import generate_palettes
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
    os.makedirs(output_dir, exist_ok=True)
    all_palettes = generate_palettes(seed, harmony_type, num_colors)

    for name, palette_data in all_palettes.items():
        print(f"\nGenerating {name} palette...")
        colors = [
            Color.from_rgb(r / 255, g / 255, b / 255)
            for r, g, b in palette_data["rgb_values"]
        ]
        visualize_palette(
            colors,
            title=f"{name.title()} Color Harmony",
            filename=os.path.join(output_dir, f"palette_{name}.png"),
        )

    json_path = os.path.join(output_dir, "palette_data.json")
    with open(json_path, "w") as f:
        json.dump(all_palettes, f, indent=2)

    print("\nGenerated palettes for all harmony types!")
    print(f"Check {output_dir} for PNG files and palette_data.json.")


def _positive_int(text: str) -> int:
    """argparse type: an integer >= 1."""
    value = int(text)
    if value < 1:
        raise argparse.ArgumentTypeError(f"must be at least 1, got {value}")
    return value


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
    parser.add_argument("--colors", type=_positive_int, default=5, help="Number of colors (default: 5)")
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
