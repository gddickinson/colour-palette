"""Palette visualization - creates PNG swatch images with gradient blends."""

from typing import List

import matplotlib.pyplot as plt
import numpy as np

from colour_palette.color import Color


def visualize_palette(
    colors: List[Color],
    title: str = "Color Palette",
    filename: str = "palette.png",
):
    """Create a visual representation of the color palette and save as PNG."""
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(12, 8), gridspec_kw={"height_ratios": [3, 1]}
    )

    # Main color blocks
    for i, color in enumerate(colors):
        ax1.add_patch(plt.Rectangle((i, 0), 1, 1, color=color.to_rgb()))

    # Add color information text
    for i, color in enumerate(colors):
        rgb = color.to_rgb()
        ax1.text(
            i + 0.5,
            0.5,
            f"RGB: {tuple(int(x*255) for x in rgb)}\nHex: {color.to_hex()}",
            ha="center",
            va="center",
            color="white" if sum(rgb) < 1.5 else "black",
        )

    ax1.set_xlim(0, len(colors))
    ax1.set_ylim(0, 1)
    ax1.axis("off")

    # Create gradient blend
    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))

    blended = np.zeros((2, 256, 3))
    for i in range(len(colors) - 1):
        start_color = np.array(colors[i].to_rgb())
        end_color = np.array(colors[i + 1].to_rgb())
        segment = np.linspace(start_color, end_color, 256 // (len(colors) - 1))
        start_idx = i * (256 // (len(colors) - 1))
        end_idx = (i + 1) * (256 // (len(colors) - 1))
        blended[:, start_idx:end_idx] = (
            segment.T.reshape(3, -1).reshape(3, 1, -1).transpose(1, 2, 0)
        )

    ax2.imshow(blended, extent=[0, len(colors), 0, 0.1])
    ax2.axis("off")

    plt.suptitle(title, fontsize=16, y=0.95)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()
