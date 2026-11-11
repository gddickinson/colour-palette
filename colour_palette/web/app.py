"""FastAPI web app for the Colour Palette Generator: serves the front end in static/ and the JSON API under /api.

Run with `python run_web.py` (http://127.0.0.1:8150, local only). `scripts/build_static.py` exports every path in
STATIC_ENDPOINTS to JSON for the GitHub Pages site, so keep that list in step with the GET routes below. On the static
site the palette endpoints are answered in the browser by colour_engine.js (a tested port of the same code).

Everything is computed by the package itself: ColorPaletteGenerator (generator.py), generate_palettes (one CLI run),
Color (color.py) and visualize_palette (visualizer.py, for the matplotlib PNG).
"""
import colorsys
import json
import os
import tempfile
import threading
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from colour_palette.color import Color, HarmonyType
from colour_palette.generator import ColorPaletteGenerator, generate_palettes

STATIC = Path(__file__).resolve().parent / "static"
ROOT = Path(__file__).resolve().parents[2]
TITLE = "Colour Palette Generator"
MAX_COLORS = 24
TEMPERATURES = ["neutral", "warm", "cool"]
# Seeds whose full CLI run is exported to the static site (42 is the CLI default and the committed palette_data.json).
DEMO_SEEDS = [42, 0, 7, 2024]

# Descriptions from the README ("Multiple Harmony Types", "Harmony Rules"); the rule and size come from generate_harmony.
HARMONIES = [
    ("complementary", "Complementary", "Two colors opposite each other", "Maximum contrast, high energy",
     "base, hue + 180°", "2"),
    ("triadic", "Triadic", "Three colors equally spaced", "Balanced, vibrant", "base, hue + 120°, hue + 240°", "3"),
    ("analogous", "Analogous", "Colors adjacent to each other", "Harmonious, comfortable",
     "base, then hue + 18° per step (0.05 of the wheel)", "n"),
    ("split_complementary", "Split-complementary", "Base color and two colors adjacent to its complement",
     "High contrast, less tension", "base, complement − 18°, complement + 18°", "3"),
    ("tetradic", "Tetradic", "Four colors forming a rectangle", "Rich, complex combinations",
     "base, hue + 90°, + 180°, + 270°", "4"),
    ("monochromatic", "Monochromatic", "Variations in saturation and brightness", "Subtle, sophisticated",
     "same hue; step i: saturation − 0.15·i, value + 0.1·i (clipped to 0-1)", "n"),
]

app = FastAPI(title=TITLE)
app.mount("/static", StaticFiles(directory=STATIC), name="static")
# generator.py seeds Python's global `random`, so palette requests must not interleave.
_rng_lock = threading.Lock()


def _with_hls(palette: dict) -> dict:
    """Add colorsys.rgb_to_hls of each colour (h, l, s in 0-1) for the HSL display."""
    hls = [list(colorsys.rgb_to_hls(*Color(*hsv).to_rgb())) for hsv in palette["hsv_values"]]
    return {**palette, "hls_values": hls}


def _harmony(name: str | None) -> str | None:
    if name in (None, "", "all"):
        return None
    if name not in {h.value for h in HarmonyType}:
        raise HTTPException(422, f"unknown harmony {name!r}")
    return name


def _base_color(hex_code: str) -> Color:
    h = hex_code.strip().lstrip("#")
    if len(h) != 6 or any(c not in "0123456789abcdefABCDEF" for c in h):
        raise HTTPException(422, f"base must be a #rrggbb colour, got {hex_code!r}")
    return Color.from_rgb(*(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)))


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/info")
def info():
    """Project summary, harmony types (README text + the rule in generate_harmony), options and defaults."""
    return {
        "title": TITLE, "version": "1",
        "description": "A Python-based creative color palette generator that creates harmonious color combinations "
                       "using established color theory principles.",
        "harmonies": [dict(zip(("id", "name", "summary", "character", "rule", "size"), h)) for h in HARMONIES],
        "temperatures": TEMPERATURES, "max_colors": MAX_COLORS, "demo_seeds": DEMO_SEEDS,
        "defaults": {"seed": 42, "colors": 5, "harmony": "all", "temperature": "neutral"},
        "temperature_hues": {"warm": "hue uniform in 0.95-1.15 (wrapped): reds, oranges, yellows",
                             "cool": "hue uniform in 0.45-0.65: cyans, blues", "neutral": "any hue"},
        "base_ranges": {"saturation": [0.6, 0.9], "value": [0.7, 0.9]},
    }


@app.get("/api/cli/{seed}")
def cli_run(seed: int, colors: int = Query(5, ge=1, le=MAX_COLORS), harmony: str | None = None,
            temperature: str = Query("neutral", pattern="^(neutral|warm|cool)$")):
    """One CLI run (`python colour_palette.py --seed SEED`): every harmony in turn from one seeded generator."""
    if abs(seed) >= 2 ** 53:
        raise HTTPException(422, "seed must be below 2^53")
    with _rng_lock:
        pal = generate_palettes(seed, _harmony(harmony), colors, temperature)
    return {"seed": seed, "colors": colors, "temperature": temperature,
            "palettes": {k: _with_hls(v) for k, v in pal.items()}, "source": "python"}


@app.get("/api/palette")
def palette(harmony: str = "complementary", colors: int = Query(5, ge=1, le=MAX_COLORS), seed: int = 42,
            temperature: str = Query("neutral", pattern="^(neutral|warm|cool)$"), base: str | None = None):
    """One palette: from a seeded random base colour (generate_palette), or from a chosen base colour (#rrggbb)."""
    h = HarmonyType(_harmony(harmony) or "complementary")
    with _rng_lock:
        if base:
            p = ColorPaletteGenerator().palette_from_base(_base_color(base), h, colors, "custom")
        else:
            if abs(seed) >= 2 ** 53:
                raise HTTPException(422, "seed must be below 2^53")
            p = ColorPaletteGenerator(seed).generate_palette(temperature, h, colors)
    return {**_with_hls(p), "seed": None if base else seed, "base": base, "source": "python"}


@app.get("/api/palette_data")
def palette_data():
    """The palette_data.json committed in the repo (output of the default CLI run, seed 42)."""
    return json.loads((ROOT / "palette_data.json").read_text())


@app.get("/api/png", response_class=Response)
def png(harmony: str = "complementary", colors: int = Query(5, ge=1, le=MAX_COLORS), seed: int = 42,
        temperature: str = Query("neutral", pattern="^(neutral|warm|cool)$"), base: str | None = None,
        cli: bool = False):
    """The palette drawn by visualize_palette (matplotlib), as the CLI's palette_<harmony>.png. Local app only.

    Same parameters as /api/palette; with cli=true the palette is the one of that harmony in a full CLI run.
    """
    import matplotlib
    matplotlib.use("Agg")
    from colour_palette.visualizer import visualize_palette
    name = _harmony(harmony) or "complementary"
    p = cli_run(seed, colors, None, temperature)["palettes"][name] if cli and not base else \
        palette(name, colors, seed, temperature, base)
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    try:
        visualize_palette([Color(*hsv) for hsv in p["hsv_values"]], title=f"{name.title()} Color Harmony",
                          filename=path)
        return Response(Path(path).read_bytes(), media_type="image/png")
    finally:
        os.unlink(path)


# GET paths (without the /api prefix) written to the static site as api/<path>.json.
STATIC_ENDPOINTS = ["/info", "/palette_data"] + [f"/cli/{s}" for s in DEMO_SEEDS]
