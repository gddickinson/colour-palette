// Generator page: the full tool. Seeded random base colour (as the CLI) or a chosen base colour; one harmony or all six;
// swatches with hex / RGB / HSV / HSL, copy buttons, analysis, gradient strip and JSON / PNG / CSS export.
// Palettes come from api('/palette') and api('/cli/<seed>'): Python on the local app, colour_engine.js on the static site.
import { route, api, app, esc, list, isStatic, $, $$ } from './core.js';
import { HARMONIES } from './colour_engine.js';
import { setInfo, harmonyName, swatches, analysis, drawGradient, bindCopy, copyText, downloadPng, downloadJson, downloadCss, INFO } from './ui.js';

const S = { mode: 'seed', seed: 42, base: '#4b5ec0', h: 'all', n: 5, t: 'neutral' };
let palettes = {}, ticket = 0;

function fromQuery(q) {
  if (q.seed !== undefined && /^-?\d+$/.test(q.seed)) { S.seed = Number(q.seed); S.mode = 'seed'; }
  if (/^#?[0-9a-f]{6}$/i.test(q.base || '')) { S.base = '#' + q.base.replace('#', '').toLowerCase(); S.mode = 'base'; }
  if (q.mode === 'seed' || q.mode === 'base') S.mode = q.mode;
  if (q.h === 'all' || HARMONIES.includes(q.h)) S.h = q.h;
  if (q.n && +q.n >= 1 && +q.n <= 24) S.n = Math.trunc(+q.n);
  if (['neutral', 'warm', 'cool'].includes(q.t)) S.t = q.t;
}

function hashFor() {
  const q = S.mode === 'base' ? { base: S.base.slice(1), h: S.h, n: S.n } : { seed: S.seed, h: S.h, n: S.n, t: S.t };
  return '#/generate?' + new URLSearchParams(q);
}

function command() {
  if (S.mode === 'seed' && S.t === 'neutral') {
    return `python colour_palette.py --seed ${S.seed} --colors ${S.n}${S.h === 'all' ? '' : ' --harmony ' + S.h}`;
  }
  const h = S.h === 'all' ? 'h' : `HarmonyType.${S.h.toUpperCase()}`, all = S.h === 'all' ? ' for h in HarmonyType' : '';
  if (S.mode === 'seed') {
    return S.h === 'all' ? `generate_palettes(seed=${S.seed}, num_colors=${S.n}, temperature="${S.t}")`
      : `ColorPaletteGenerator(seed=${S.seed}).generate_palette("${S.t}", ${h}, ${S.n})`;
  }
  const base = `Color.from_rgb(${S.base.slice(1).match(/../g).map(x => `0x${x}/255`).join(', ')})`;
  return `${all ? '[' : ''}ColorPaletteGenerator().palette_from_base(${base}, ${h}, ${S.n})${all}${all ? ']' : ''}`;
}

async function compute() {
  const qn = `colors=${S.n}`;
  if (S.mode === 'seed') {
    if (S.h === 'all') return (await api(`/cli/${S.seed}?${qn}&temperature=${S.t}`)).palettes;
    return { [S.h]: await api(`/palette?harmony=${S.h}&${qn}&seed=${S.seed}&temperature=${S.t}`) };
  }
  const hs = S.h === 'all' ? HARMONIES : [S.h], base = encodeURIComponent(S.base);
  const ps = await Promise.all(hs.map(h => api(`/palette?harmony=${h}&${qn}&base=${base}`)));
  return Object.fromEntries(hs.map((h, i) => [h, ps[i]]));
}

function pngLink(name) {
  const q = S.mode === 'base' ? `base=${encodeURIComponent(S.base)}` : `seed=${S.seed}&temperature=${S.t}${S.h === 'all' ? '&cli=true' : ''}`;
  return `api/png?harmony=${name}&colors=${S.n}&${q}`;
}

function paletteBlock(name, p) {
  const h = INFO.harmonies.find(x => x.id === name);
  return `<section class="pal" data-pal="${name}">
    <header><h2>${esc(harmonyName(name))}</h2><span class="small mute">${esc(h.character)} · ${esc(h.rule)}</span>
      <span class="acts"><button class="alt" data-act="hexes" aria-label="Copy all ${esc(h.name)} hex codes">copy hex</button>
      <button class="alt" data-act="png" aria-label="Download ${esc(h.name)} PNG">PNG</button>
      ${isStatic() ? '' : `<a class="btn alt" href="${pngLink(name)}" target="_blank" rel="noopener" title="Drawn by visualize_palette (matplotlib), as the CLI">matplotlib PNG</a>`}</span>
    </header>
    ${swatches(p)}
    <canvas class="grad" role="img" aria-label="${esc(h.name)} gradient blend"></canvas>
    ${analysis(p)}
  </section>`;
}

async function update() {
  const my = ++ticket, out = $('#out');
  history.replaceState(null, '', hashFor());
  $('#cmd').textContent = command();
  let pals;
  try { pals = await compute(); } catch (e) { out.innerHTML = `<p class="err">${esc(e.message)}</p>`; return; }
  if (my !== ticket) return;
  palettes = pals;
  out.innerHTML = list(Object.entries(pals), ([k, p]) => paletteBlock(k, p));
  $$('.pal', out).forEach(sec => drawGradient($('canvas.grad', sec), pals[sec.dataset.pal].hsv_values));
  const src = Object.values(pals)[0]?.source || (S.mode === 'seed' && S.h === 'all' ? 'cli' : '');
  $('#src').textContent = isStatic() ? 'computed in your browser by colour_engine.js' : `computed by the Python package (${src || 'python'})`;
}

function controls() {
  const sel = (id, opts, v) => `<select id="${id}">${list(opts, ([val, lab]) => `<option value="${val}"${val === v ? ' selected' : ''}>${esc(lab)}</option>`)}</select>`;
  return `<div class="controls">
    <label>Base colour</label>
    <div class="seg" role="group" aria-label="Base colour source"><button data-mode="seed">From a seed</button><button data-mode="base">Pick colour</button></div>
    <div id="seedbox"><label for="seed">Seed</label>
      <div class="inline"><input id="seed" type="number" step="1" value="${S.seed}"><button id="reseed" class="alt" title="Pick a random seed" aria-label="Random seed">↻</button></div>
      <label for="temp">Temperature preference</label>${sel('temp', INFO.temperatures.map(t => [t, t]), S.t)}
      <p class="small mute" id="tempnote"></p></div>
    <div id="basebox"><label for="basehex">Base colour (#rrggbb)</label>
      <div class="inline"><input id="basepick" type="color" value="${S.base}" aria-label="Colour picker"><input id="basehex" value="${S.base}" maxlength="7" spellcheck="false"></div></div>
    <label for="harm">Harmony</label>${sel('harm', [['all', 'All six (as the CLI)'], ...INFO.harmonies.map(h => [h.id, h.name])], S.h)}
    <label for="ncol">Colours <b id="nval">${S.n}</b></label><input id="ncol" type="range" min="1" max="${INFO.max_colors}" value="${S.n}">
    <p class="small mute">Complementary gives at most 2 colours, triadic and split-complementary 3, tetradic 4.</p>
    <button id="xjson">JSON</button><button id="xcss" class="alt" title="Web-only convenience: CSS custom properties">CSS</button>
    <button id="xlink" class="alt">Copy link</button>
    <div class="cmd" id="cmd" title="The same palettes from Python"></div>
    <p class="small mute" id="src"></p>
  </div>`;
}

function syncControls() {
  $$('[data-mode]').forEach(b => { b.classList.toggle('on', b.dataset.mode === S.mode); b.setAttribute('aria-pressed', b.dataset.mode === S.mode); });
  $('#seedbox').hidden = S.mode !== 'seed'; $('#basebox').hidden = S.mode !== 'base';
  $('#tempnote').textContent = INFO.temperature_hues[S.t] + (S.t === 'neutral' ? '' : ' (Python API option; the CLI always uses neutral)');
}

route('generate', async (args, query) => {
  setInfo(await api('/info'));
  fromQuery(query);
  app().innerHTML = `<h1 class="glow">Generator</h1>
    <p class="lead">The same seed gives the same palettes as <code>python colour_palette.py --seed N</code>. Click any value to copy it.</p>
    <div class="gen">${controls()}<div id="out" aria-live="polite"></div></div>`;
  syncControls();
  const go = () => { syncControls(); update(); };
  $$('[data-mode]').forEach(b => b.addEventListener('click', () => { S.mode = b.dataset.mode; go(); }));
  $('#seed').addEventListener('change', e => { if (Number.isSafeInteger(+e.target.value)) { S.seed = +e.target.value; go(); } });
  $('#reseed').addEventListener('click', () => { S.seed = Math.floor(Math.random() * 100000); $('#seed').value = S.seed; go(); });
  $('#temp').addEventListener('change', e => { S.t = e.target.value; go(); });
  $('#harm').addEventListener('change', e => { S.h = e.target.value; go(); });
  $('#ncol').addEventListener('input', e => { S.n = +e.target.value; $('#nval').textContent = S.n; go(); });
  $('#basepick').addEventListener('input', e => { S.base = e.target.value; $('#basehex').value = S.base; go(); });
  $('#basehex').addEventListener('change', e => {
    const v = e.target.value.trim().replace(/^#?/, '#').toLowerCase();
    if (/^#[0-9a-f]{6}$/.test(v)) { S.base = v; $('#basepick').value = v; go(); } else e.target.value = S.base;
  });
  $('#xjson').addEventListener('click', () => downloadJson(palettes));
  $('#xcss').addEventListener('click', () => downloadCss(palettes));
  $('#xlink').addEventListener('click', () => copyText(location.href));
  const out = $('#out');
  bindCopy(out);
  out.addEventListener('click', e => {
    const b = e.target.closest('[data-act]'); if (!b) return;
    const name = b.closest('.pal').dataset.pal, p = palettes[name];
    if (b.dataset.act === 'hexes') copyText(p.colors.join(', '));
    if (b.dataset.act === 'png') downloadPng(p, name);
  });
  await update();
});
