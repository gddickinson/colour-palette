// Shared palette UI: swatch cards with hex / RGB / HSV / HSL and copy buttons, gradient strip, analysis line, exports.
import { esc, list, download, $ } from './core.js';
import { color, gradientBlend, toRgb } from './colour_engine.js';

export let INFO = null;
export const setInfo = i => { INFO = i; };
export const harmonyName = id => (INFO?.harmonies.find(h => h.id === id)?.name) || id;
const pct = x => `${Math.round(x * 100)}%`;
const deg = h => `${Math.round(h * 360) % 360}°`;
export const fmtHsv = ([h, s, v]) => `${deg(h)}, ${pct(s)}, ${pct(v)}`;
export const fmtHsl = ([h, l, s]) => `hsl(${deg(h).replace('°', '')} ${pct(s)} ${pct(l)})`;
export const fmtRgb = rgb => `rgb(${rgb.join(', ')})`;
// visualize_palette's label colour rule: white text when R + G + B < 1.5.
export const inkFor = hsv => (toRgb(color(...hsv)).reduce((a, b) => a + b, 0) < 1.5 ? '#fff' : '#000');

function row(label, text) {
  return `<dt>${label}</dt><dd>${esc(text)}</dd><button class="cp" data-copy="${esc(text)}" aria-label="Copy ${label} ${esc(text)}">copy</button>`;
}

export function swatches(p) {
  return `<div class="sw">${list(p.colors, (hex, i) => `<div class="chip">
    <div class="block" style="background:${hex};color:${inkFor(p.hsv_values[i])}">${i === 0 ? 'base' : i + 1}</div>
    <dl>${row('HEX', hex)}${row('RGB', fmtRgb(p.rgb_values[i]))}${row('HSV', fmtHsv(p.hsv_values[i]))}${row('HSL', fmtHsl(p.hls_values[i]))}</dl>
  </div>`)}</div>`;
}

export function analysis(p) {
  const a = p.analysis, f = x => x.toFixed(3);
  return `<p class="ana">brightness <b>${f(a.brightness)}</b> · temperature <b>${esc(a.temperature)}</b> ·
    contrast <b>${f(a.contrast)}</b> · harmony level <b>${f(a.harmony_level)}</b></p>`;
}

// Draw the gradient strip (visualizer.gradient_blend) into a canvas 256 px wide.
export function drawGradient(canvas, hsvs) {
  const g = gradientBlend(hsvs.map(h => color(...h))), ctx = canvas.getContext('2d');
  canvas.width = g.length; canvas.height = 1;
  const img = ctx.createImageData(g.length, 1);
  g.forEach((rgb, i) => { rgb.forEach((x, k) => { img.data[i * 4 + k] = Math.round(x * 255); }); img.data[i * 4 + 3] = 255; });
  ctx.putImageData(img, 0, 0);
}

// --- clipboard ---------------------------------------------------------------------------------------------------
export function toast(msg) {
  const t = $('#toast'); if (!t) return;
  t.textContent = msg; t.classList.add('show');
  clearTimeout(toast.id); toast.id = setTimeout(() => t.classList.remove('show'), 1400);
}
export async function copyText(text) {
  try { await navigator.clipboard.writeText(text); }
  catch {
    const ta = Object.assign(document.createElement('textarea'), { value: text });
    document.body.appendChild(ta); ta.select(); document.execCommand('copy'); ta.remove();
  }
  toast(`copied ${text.length > 40 ? text.slice(0, 40) + '…' : text}`);
}
export function bindCopy(root) {
  root.addEventListener('click', e => { const b = e.target.closest('[data-copy]'); if (b) copyText(b.dataset.copy); });
}

// --- exports -----------------------------------------------------------------------------------------------------
const PY_KEYS = ['colors', 'rgb_values', 'hsv_values', 'analysis', 'harmony_type', 'temperature'];
// Same structure as the CLI's palette_data.json: {harmony: {colors, rgb_values, hsv_values, analysis, ...}}.
export function paletteJson(palettes) {
  const out = {};
  for (const [k, p] of Object.entries(palettes)) out[k] = Object.fromEntries(PY_KEYS.map(key => [key, p[key]]));
  return JSON.stringify(out, null, 2);
}

// CSS custom properties (a web-only convenience; the Python package writes PNG and JSON).
export function paletteCss(palettes) {
  const lines = [];
  for (const [k, p] of Object.entries(palettes)) {
    const name = k.replace(/_/g, '-');
    p.colors.forEach((hex, i) => lines.push(`  --${name}-${i + 1}: ${hex};`));
  }
  return `/* Colour Palette Generator */\n:root {\n${lines.join('\n')}\n}\n`;
}

// PNG drawn in the browser with the layout of visualizer.visualize_palette: title, swatch blocks with RGB/Hex labels,
// gradient strip below. (The local app can also return the matplotlib original: api/png.)
export function palettePng(p, title) {
  const W = 1200, H = 760, pad = 30, n = p.colors.length, bw = (W - 2 * pad) / n, top = 70, bh = 480;
  const c = Object.assign(document.createElement('canvas'), { width: W, height: H });
  const ctx = c.getContext('2d');
  ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H);
  ctx.fillStyle = '#000'; ctx.font = '28px sans-serif'; ctx.textAlign = 'center'; ctx.fillText(title, W / 2, 44);
  p.colors.forEach((hex, i) => {
    ctx.fillStyle = hex; ctx.fillRect(pad + i * bw, top, Math.ceil(bw), bh);
    ctx.fillStyle = inkFor(p.hsv_values[i]); ctx.font = `${n > 8 ? 12 : 16}px sans-serif`;
    ctx.fillText(`RGB: (${p.rgb_values[i].join(', ')})`, pad + (i + 0.5) * bw, top + bh / 2 - 6);
    ctx.fillText(`Hex: ${hex}`, pad + (i + 0.5) * bw, top + bh / 2 + 18);
  });
  const g = document.createElement('canvas'); drawGradient(g, p.hsv_values);
  ctx.imageSmoothingEnabled = true; ctx.drawImage(g, pad, top + bh + 60, W - 2 * pad, 80);
  return new Promise(res => c.toBlob(res, 'image/png'));
}

export async function downloadPng(p, name) {
  download(`palette_${name}.png`, await palettePng(p, `${name.replace(/_/g, ' ').replace(/\b\w/g, m => m.toUpperCase())} Color Harmony`));
}
export const downloadJson = pals => download('palette_data.json', paletteJson(pals), 'application/json');
export const downloadCss = pals => download('palette.css', paletteCss(pals), 'text/css');
