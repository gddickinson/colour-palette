// Harmonies page: each of the six rules drawn on a hue wheel for one base colour (angle = hue, radius = saturation),
// with the README description and the exact step generate_harmony uses.
import { route, api, app, esc, list, $ } from './core.js';
import { setInfo, swatches, bindCopy, fmtHsv } from './ui.js';

let base = '#c84a9b', count = 5;

function wheel(p) {
  const pos = ([h, s]) => [50 + 46 * s * Math.sin(2 * Math.PI * h), 50 - 46 * s * Math.cos(2 * Math.PI * h)];
  const pts = p.hsv_values.map(pos);
  const poly = pts.length > 2 ? `<polygon points="${pts.map(([x, y]) => `${x},${y}`).join(' ')}" fill="none" stroke="#05060c" stroke-width="1.2" stroke-dasharray="2 2"/>`
    : pts.length === 2 ? `<line x1="${pts[0][0]}" y1="${pts[0][1]}" x2="${pts[1][0]}" y2="${pts[1][1]}" stroke="#05060c" stroke-width="1.2" stroke-dasharray="2 2"/>` : '';
  return `<div class="wheel" role="img" aria-label="Hue wheel: ${p.colors.length} colours at ${p.hsv_values.map(fmtHsv).join('; ')}">
    <svg viewBox="0 0 100 100" aria-hidden="true">${poly}</svg>
    ${list(p.colors, (c, i) => `<span class="dot${i ? '' : ' base'}" style="left:${pts[i][0]}%;top:${pts[i][1]}%;background:${c}" title="${c}"></span>`)}
  </div>`;
}

async function draw(info) {
  const pals = await Promise.all(info.harmonies.map(h => api(`/palette?harmony=${h.id}&colors=${count}&base=${encodeURIComponent(base)}`)));
  $('#wheels').innerHTML = list(info.harmonies, (h, i) => `<div class="card">
    <b>${esc(h.name)}</b><small>${esc(h.summary)} · ${esc(h.character)}</small>
    ${wheel(pals[i])}
    <p class="small"><span class="mute">Rule:</span> ${esc(h.rule)}. <span class="mute">Colours:</span> ${h.size === 'n' ? 'as many as asked' : 'at most ' + h.size}.</p>
    <details><summary class="small">Values</summary>${swatches(pals[i])}</details>
    <a class="small" href="#/generate?base=${base.slice(1)}&h=${h.id}&n=${count}">Open in the generator →</a>
  </div>`);
}

route('harmonies', async (args, query) => {
  const info = await api('/info');
  setInfo(info);
  if (/^[0-9a-f]{6}$/i.test(query.base || '')) base = '#' + query.base.toLowerCase();
  app().innerHTML = `<h1 class="glow">Harmonies</h1>
    <p class="lead">Six ways the generator picks colours around a base colour. On each wheel the angle is the hue and the
    distance from the centre is the saturation; the large dot is the base colour.</p>
    <div class="row" style="max-width:560px">
      <div><label for="hb">Base colour</label><div class="inline"><input type="color" id="hb" value="${base}" aria-label="Base colour picker"><input id="hbx" value="${base}" maxlength="7" aria-label="Base colour hex"></div></div>
      <div><label for="hn">Colours (analogous, monochromatic) <b id="hnv">${count}</b></label><input id="hn" type="range" min="1" max="12" value="${count}"></div>
    </div>
    <div class="wheels" id="wheels" style="margin-top:16px"></div>
    <h2>Temperature preference</h2>
    <p>A random base colour has saturation ${info.base_ranges.saturation.join('-')} and value ${info.base_ranges.value.join('-')};
    its hue depends on the temperature preference:</p>
    <ul>${list(Object.entries(info.temperature_hues), ([k, v]) => `<li><b>${esc(k)}</b>: ${esc(v)}</li>`)}</ul>`;
  const set = v => { base = v; $('#hb').value = v; $('#hbx').value = v; history.replaceState(null, '', `#/harmonies?base=${v.slice(1)}`); draw(info); };
  $('#hb').addEventListener('input', e => set(e.target.value));
  $('#hbx').addEventListener('change', e => { const v = e.target.value.trim().replace(/^#?/, '#').toLowerCase(); /^#[0-9a-f]{6}$/.test(v) ? set(v) : (e.target.value = base); });
  $('#hn').addEventListener('input', e => { count = +e.target.value; $('#hnv').textContent = count; draw(info); });
  bindCopy($('#wheels'));
  await draw(info);
});
