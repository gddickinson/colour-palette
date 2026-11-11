// About page: what the generator does (from the README and the code), how to run the CLI and the web app, credits.
import { route, api, app, esc, list, isStatic } from './core.js';
import { setInfo } from './ui.js';

route('about', async () => {
  const info = await api('/info');
  setInfo(info);
  app().innerHTML = `<h1 class="glow">About</h1>
  <p class="lead">${esc(info.description)}</p>
  <div class="two">
    <div class="panel"><h3>How a palette is made</h3>
      <p>A base colour is drawn at random (Python's <code>random</code>, seeded) in HSV: saturation
      ${info.base_ranges.saturation.join('-')}, value ${info.base_ranges.value.join('-')}, and a hue that depends on the
      temperature preference. A harmony rule then derives the other colours:</p>
      <ul class="small">${list(info.harmonies, h => `<li><b>${esc(h.name)}</b>: ${esc(h.rule)}</li>`)}</ul>
      <p class="small">The command-line tool runs all six harmonies in turn from one seeded generator, so its triadic
      palette for seed 42 is not the same as a triadic palette generated alone with seed 42. The generator page does the
      same when "All six" is selected.</p></div>
    <div class="panel"><h3>Analysis</h3>
      <ul class="small">
        <li><b>Brightness</b>: mean of (R + G + B) / 3 over the colours (0-1)</li>
        <li><b>Temperature</b>: "warm" if the mean of R − B is positive, else "cool"</li>
        <li><b>Contrast</b>: brightest minus darkest colour brightness</li>
        <li><b>Harmony level</b>: min(1, 2 × contrast)</li>
      </ul>
      <h3>Colour values</h3>
      <p class="small">HSV is the generator's own space. RGB and hex come from <code>colorsys.hsv_to_rgb</code> and are
      truncated to 0-255 (as <code>Color.to_hex</code> does); HSL is <code>colorsys.rgb_to_hls</code> of the same colour.
      Exports: JSON in the format of <code>palette_data.json</code>, a PNG laid out like <code>palette_*.png</code>
      ${isStatic() ? '' : '(or the matplotlib original from the local app)'}, and CSS custom properties (a web-only extra).</p></div>
  </div>
  <h2>Run it</h2>
  <div class="two">
    <div><h3>Command line</h3>
      <pre>git clone https://github.com/gddickinson/colour-palette.git
cd colour-palette
pip install -r requirements.txt
python colour_palette.py --seed 42 --colors 5
python colour_palette.py --harmony triadic --output-dir out</pre>
      <p class="small">Writes <code>palette_&lt;harmony&gt;.png</code> and <code>palette_data.json</code>.</p></div>
    <div><h3>Web app (local)</h3>
      <pre>pip install -r requirements-web.txt
python run_web.py        # http://127.0.0.1:8150</pre>
      <p class="small">The local app serves palettes from the Python package and can draw the matplotlib PNG. This
      static site needs no server: the generator is the JavaScript port, tested to give the same numbers.</p></div>
  </div>
  <h2>Credits</h2>
  <p>Colour Palette Generator by George Dickinson, built with numpy and matplotlib, using colour-theory principles from
  traditional art and design and HSV colour-space calculations. Built with AI assistance from
  <a href="https://claude.com/">Claude (Anthropic)</a>. MIT licence.
  <a href="https://github.com/gddickinson/colour-palette">Source on GitHub</a>.</p>`;
});
