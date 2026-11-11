"""Compute reference values with the repo's Python code for colour_palette/web/static/colour_engine.test.mjs.

Writes tests/fixtures/colour_engine.json; tests/test_web.py recomputes it and checks the committed copy is current
(numbers compared with a tolerance), so the JS engine is always tested against the current Python package.

Run: python scripts/make_engine_fixture.py            (print a summary)
     python scripts/make_engine_fixture.py --write    (rewrite the fixture file)
"""
import argparse
import colorsys
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from colour_palette.color import Color, HarmonyType  # noqa: E402
from colour_palette.generator import ColorPaletteGenerator, generate_palettes  # noqa: E402
from colour_palette.visualizer import gradient_blend  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "colour_engine.json"
SEEDS = [0, 1, 7, 42, 99, 123, 2024, 4294967295, 4294967296, 9007199254740991]
BASES = [(0.0, 1.0, 1.0), (0.25, 0.8, 0.9), (0.6394, 0.6075, 0.755), (0.97, 0.66, 0.71), (0.5, 0.0, 0.5),
         (0.999999, 0.9, 0.85), (1 / 6, 0.75, 0.8), (0.83, 0.3, 0.2)]
HSV = [(0.0, 0.0, 0.0), (1 / 3, 1.0, 1.0), (0.5, 0.5, 0.5), (0.95, 0.61, 0.73), (0.999999, 0.2, 0.9),
       (-0.3, 1.4, -0.2), (1.25, 0.5, 1.2), (2 / 3, 0.123, 0.987), (5 / 6, 1.0, 0.01)]
RGB = [(0, 0, 0), (1, 1, 1), (1, 0, 0), (0, 1, 0), (0, 0, 1), (0.2, 0.4, 0.6), (0.9, 0.1, 0.5), (0.75, 0.75, 0.2),
       (75 / 255, 94 / 255, 192 / 255), (0.3, 0.3, 0.29999999), (0.6, 0.55, 0.9)]
HEXES = ["#4b5ec0", "#ff0000", "#000000", "#ffffff", "#7f7f7f", "#c84a9b", "#12ab34"]


def mt_cases():
    out = []
    for s in SEEDS:
        random.seed(s)
        out.append({"seed": s, "random": [random.random() for _ in range(8)],
                    "uniform": [random.uniform(0.6, 0.9) for _ in range(3)]})
    return out


def conversions():
    return {
        "color": [[h, s, v, *(lambda c: [c.h, c.s, c.v, c.to_hex(), list(c.to_rgb())])(Color(h, s, v))]
                  for h, s, v in HSV],
        "rgb_to_hsv": [[*rgb, *colorsys.rgb_to_hsv(*rgb)] for rgb in RGB],
        "rgb_to_hls": [[*rgb, *colorsys.rgb_to_hls(*rgb)] for rgb in RGB],
        "hex_to_hsv": [[h, *(lambda c: [c.h, c.s, c.v])(Color.from_rgb(*(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))))]
                       for h in HEXES],
    }


def harmony_cases():
    gen = ColorPaletteGenerator()
    out = []
    for base in BASES:
        for harmony in HarmonyType:
            for n in (1, 2, 3, 5, 8, 12):
                out.append({"base": list(base), "harmony": harmony.value, "n": n,
                            "palette": gen.palette_from_base(Color(*base), harmony, n)})
    return out


def palette_cases():
    out = []
    for seed in SEEDS[:7]:
        for temp in ("neutral", "warm", "cool"):
            for harmony, n in (("analogous", 9), ("monochromatic", 4), ("tetradic", 5)):
                gen = ColorPaletteGenerator(seed)
                out.append({"seed": seed, "temperature": temp, "harmony": harmony, "n": n,
                            "palette": gen.generate_palette(temp, HarmonyType(harmony), n)})
    return out


def cli_runs():
    return [{"seed": s, "n": n, "palettes": generate_palettes(s, None, n)} for s in (0, 7, 42, 2024, -5, 2 ** 40 + 3) for n in (3, 5)]


def gradients():
    out = []
    for n in (1, 2, 4, 7):
        colors = [Color(*BASES[i]) for i in range(n)]
        g = gradient_blend(colors)[0]
        out.append({"bases": [list(b) for b in BASES[:n]], "cols": {str(j): list(g[j]) for j in (0, 1, 84, 85, 200, 255)}})
    return out


def build():
    return json.loads(json.dumps({"mt": mt_cases(), "conversions": conversions(), "harmonies": harmony_cases(),
                                  "palettes": palette_cases(), "cli": cli_runs(), "gradients": gradients()}))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    data = build()
    if ap.parse_args().write:
        FIXTURE.parent.mkdir(parents=True, exist_ok=True)
        FIXTURE.write_text(json.dumps(data, separators=(",", ":")) + "\n")
        print(f"wrote {FIXTURE}")
    print({k: len(v) for k, v in data.items() if isinstance(v, list)})


if __name__ == "__main__":
    main()
