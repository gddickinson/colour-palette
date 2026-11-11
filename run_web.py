"""Start the Colour Palette Generator web app on http://127.0.0.1:8150 (local only).

Run: python run_web.py [--port 8150]
Needs: pip install -r requirements-web.txt
"""
import argparse

import uvicorn

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8150)
    port = ap.parse_args().port
    print(f"Colour Palette Generator web app: http://127.0.0.1:{port}")
    uvicorn.run("colour_palette.web.app:app", host="127.0.0.1", port=port)
