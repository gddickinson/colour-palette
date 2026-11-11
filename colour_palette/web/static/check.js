// Cross-check page: palettes from the Python package (live on the local app; exported at build time on the static
// site) against colour_engine.js for the same seeds, plus the palette_data.json committed in the repo.
import { route, api, app, esc, list, isStatic, $ } from './core.js';
import { generatePalettes } from './colour_engine.js';
import { setInfo, harmonyName } from './ui.js';

// Compare two {harmony: palette} maps: hex/RGB must match exactly; floats by their largest absolute difference.
function compare(py, js) {
  let hexSame = 0, hexAll = 0, maxDiff = 0, tempOk = true;
  for (const [k, p] of Object.entries(py)) {
    const q = js[k];
    p.colors.forEach((c, i) => { hexAll++; if (q && c === q.colors[i] && String(p.rgb_values[i]) === String(q.rgb_values[i])) hexSame++; });
    const fl = x => [...x.hsv_values.flat(), x.analysis.brightness, x.analysis.contrast, x.analysis.harmony_level];
    if (q) fl(p).forEach((v, i) => { maxDiff = Math.max(maxDiff, Math.abs(v - fl(q)[i])); });
    if (!q || p.analysis.temperature !== q.analysis.temperature) tempOk = false;
  }
  return { hexSame, hexAll, maxDiff, ok: tempOk && hexSame === hexAll && maxDiff < 1e-12 };
}

function rowHtml(label, py, c) {
  return `<tr><td>${label}</td><td>${list(Object.entries(py), ([k, p]) => `<span class="bar" style="height:14px;margin:2px 0" title="${esc(harmonyName(k))}">${list(p.colors, x => `<span style="background:${x}"></span>`)}</span>`)}</td>
    <td>${c.hexSame}/${c.hexAll}</td><td>${c.maxDiff === 0 ? '0 (bit-identical)' : c.maxDiff.toExponential(1)}</td>
    <td class="${c.ok ? 'ok' : 'err'}">${c.ok ? 'match' : 'differs'}</td></tr>`;
}

const HEAD = '<thead><tr><th>Run</th><th>Palettes (Python)</th><th>hex + RGB equal</th><th>max float diff</th><th></th></tr></thead>';

route('check', async () => {
  const info = await api('/info');
  setInfo(info);
  app().innerHTML = `<h1 class="glow">Cross-check</h1>
    <p class="lead">The browser generator (<code>colour_engine.js</code>) is a port of <code>colour_palette</code>, including
    Python's Mersenne Twister seeding, <code>colorsys</code>, NumPy's pairwise mean and Python 3.12's compensated
    <code>sum()</code>, so the same seed gives the same palettes. Here it is compared with the Python output for whole
    command-line runs (all six harmonies, 5 colours).</p>
    <div class="scroll"><table class="cmp" id="t1">${HEAD}<tbody></tbody></table></div>
    <h2>The committed palette_data.json</h2>
    <p id="pd" class="small"></p>
    <div id="live"></div>
    <p class="small mute">A node test (<code>colour_engine.test.mjs</code>) runs the same comparison on ${'>'}5,000 numbers
    from <code>scripts/make_engine_fixture.py</code>: every harmony for eight base colours and six palette sizes, every
    temperature, colour-space conversions and the PNG gradient strip.</p>`;
  const rows = [];
  for (const seed of info.demo_seeds) {
    const py = (await api(`/cli/${seed}`)).palettes;
    rows.push(rowHtml(`seed ${seed}`, py, compare(py, generatePalettes(seed, null, 5))));
  }
  $('#t1 tbody').innerHTML = rows.join('');
  const pd = await api('/palette_data'), c = compare(pd, generatePalettes(42, null, 5));
  $('#pd').innerHTML = `Seed 42, written by an earlier version of the code: ${c.hexSame}/${c.hexAll} hex codes and RGB values equal;
    largest float difference ${c.maxDiff.toExponential(1)} (only the last digits of the analysis contrast differ).`;
  if (isStatic()) {
    $('#live').innerHTML = `<p class="static-note">On the static site the Python side is the runs exported at build time
      (seeds ${info.demo_seeds.join(', ')}). The local app compares any seed live.</p>`;
    return;
  }
  $('#live').innerHTML = `<h2>Random seeds, live</h2><button id="more">Compare 10 random seeds</button>
    <div class="scroll"><table class="cmp" id="t2">${HEAD}<tbody></tbody></table></div>`;
  $('#more').addEventListener('click', async () => {
    const out = [];
    for (let i = 0; i < 10; i++) {
      const seed = Math.floor(Math.random() * 2 ** 40), n = 1 + Math.floor(Math.random() * 12);
      const py = (await api(`/cli/${seed}?colors=${n}`, { fresh: true })).palettes;
      out.push(rowHtml(`seed ${seed}, ${n} colours`, py, compare(py, generatePalettes(seed, null, n))));
    }
    $('#t2 tbody').innerHTML = out.join('');
  });
});
