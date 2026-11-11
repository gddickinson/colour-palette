"""Web interface tests: every exported endpoint answers, the static build is complete, and the JS engine tests pass.

Run: python -m pytest -q tests/test_web.py
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from colour_palette.web.app import STATIC, STATIC_ENDPOINTS, app  # noqa: E402

client = TestClient(app)


def test_index_served():
    r = client.get("/")
    assert r.status_code == 200 and "static/main.js" in r.text


@pytest.mark.parametrize("path", STATIC_ENDPOINTS)
def test_endpoint(path):
    r = client.get("/api" + path)
    assert r.status_code == 200, r.text
    assert r.json() is not None


def test_static_build(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_static
    build_static.build(tmp_path / "site")
    assert (tmp_path / "site" / "index.html").read_text().count("APP_STATIC") == 1
    for path in STATIC_ENDPOINTS:
        assert (tmp_path / "site" / "api" / (path.strip("/") + ".json")).exists()


def test_static_assets_referenced_exist():
    html = (STATIC / "index.html").read_text()
    for name in ("style.css", "main.js"):
        assert f"static/{name}" in html and (STATIC / name).exists()


@pytest.mark.skipif(not shutil.which("node"), reason="node not installed")
def test_js_engine():
    tests = sorted(STATIC.glob("*.test.mjs"))
    for t in tests:
        r = subprocess.run(["node", str(t)], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr


# --- project-specific API tests ------------------------------------------------------------------------------------
import json  # noqa: E402


def test_cli_run_matches_committed_palette_data():
    """/cli/42 is the default CLI run, i.e. the committed palette_data.json (floats to rounding)."""
    run = client.get("/api/cli/42").json()["palettes"]
    committed = json.loads((ROOT / "palette_data.json").read_text())
    assert list(run) == list(committed)
    for k, p in committed.items():
        assert run[k]["colors"] == p["colors"] and run[k]["rgb_values"] == p["rgb_values"]
        assert run[k]["analysis"]["contrast"] == pytest.approx(p["analysis"]["contrast"], rel=1e-9, abs=1e-12)


def test_palette_seeded_and_from_base():
    p = client.get("/api/palette?harmony=triadic&colors=5&seed=7").json()
    assert len(p["colors"]) == 3 and len(p["hls_values"]) == 3 and p["seed"] == 7
    b = client.get("/api/palette", params={"harmony": "complementary", "base": "#ff0000"}).json()
    assert b["colors"] == ["#ff0000", "#00ffff"] and b["hls_values"][0] == [0.0, 0.5, 1.0]


@pytest.mark.parametrize("query", ["harmony=nope", "colors=0", "colors=99", "temperature=hot", "base=%23zzzzzz"])
def test_palette_rejects_bad_input(query):
    assert client.get("/api/palette?" + query).status_code == 422


def test_png_is_the_matplotlib_visualizer():
    r = client.get("/api/png?harmony=tetradic&seed=42&cli=true")
    assert r.status_code == 200 and r.headers["content-type"] == "image/png" and r.content[:4] == b"\x89PNG"


def test_engine_fixture_is_current():
    """The fixture the node test uses must equal what the current Python code computes (numbers to rel 1e-9)."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import make_engine_fixture
    fresh = make_engine_fixture.build()
    committed = json.loads(make_engine_fixture.FIXTURE.read_text())

    def same(a, b, path="$"):
        if isinstance(a, dict):
            assert a.keys() == b.keys(), path
            for k in a:
                same(a[k], b[k], f"{path}.{k}")
        elif isinstance(a, list):
            assert len(a) == len(b), path
            for i, (x, y) in enumerate(zip(a, b)):
                same(x, y, f"{path}[{i}]")
        elif isinstance(a, float) or isinstance(b, float):
            assert a == pytest.approx(b, rel=1e-9, abs=1e-12), path
        else:
            assert a == b, path
    same(fresh, committed)
