"""Palette visualization - creates PNG swatch images with gradient blends."""

from typing import List

import matplotlib.pyplot as plt
import numpy as np

from colour_palette.color import Color


def gradient_blend(colors: List[Color], width: int = 256) -> np.ndarray:
    """Return a (2, width, 3) RGB strip blending linearly through the colors in order.

    Segment boundaries are spread over the full width, so every column is filled (a single color gives a solid strip).
    """
    blended = np.zeros((2, width, 3))
    rgbs = [np.array(c.to_rgb()) for c in colors]
    if len(rgbs) == 1:
        blended[:] = rgbs[0]
        return blended
    n_seg = len(rgbs) - 1
    for i in range(n_seg):
        start_idx = i * width // n_seg
        end_idx = (i + 1) * width // n_seg
        blended[:, start_idx:end_idx] = np.linspace(rgbs[i], rgbs[i + 1], end_idx - start_idx)
    return blended


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
            f"RGB: {color.to_rgb255()}\nHex: {color.to_hex()}",
            ha="center",
            va="center",
            color="white" if sum(rgb) < 1.5 else "black",
        )

    ax1.set_xlim(0, len(colors))
    ax1.set_ylim(0, 1)
    ax1.axis("off")

    ax2.imshow(gradient_blend(colors), extent=[0, len(colors), 0, 0.1])
    ax2.axis("off")

    plt.suptitle(title, fontsize=16, y=0.95)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()
