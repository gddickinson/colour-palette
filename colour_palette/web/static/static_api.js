// Static-site data layer: answers api() calls without a server. /info, /palette_data and the demo /cli/<seed> runs are
// JSON files exported by scripts/build_static.py (computed by the Python package); /palette and any other /cli/<seed>
// are computed in the browser by colour_engine.js, which reproduces the Python output (see colour_engine.test.mjs).
import { HARMONIES, TEMPERATURES, PaletteGenerator, color, fromHex, generatePalettes, rgbToHls, toRgb } from './colour_engine.js';

const MAX_COLORS = 24;
const files = new Map();
function file(rel) {
  if (!files.has(rel)) {
    files.set(rel, fetch('api/' + rel + '.json').then(r => { if (!r.ok) throw new Error(`${r.status} ${rel}`); return r.json(); }));
  }
  return files.get(rel);
}

const withHls = p => ({ ...p, hls_values: p.hsv_values.map(h => rgbToHls(...toRgb(color(...h)))) });

function opts(q) {
  const colors = q.has('colors') ? Number(q.get('colors')) : 5;
  if (!Number.isInteger(colors) || colors < 1 || colors > MAX_COLORS) throw new Error(`colors must be 1-${MAX_COLORS}`);
  const temperature = q.get('temperature') || 'neutral';
  if (!TEMPERATURES.includes(temperature)) throw new Error(`unknown temperature ${temperature}`);
  let harmony = q.get('harmony') || null;
  if (harmony === 'all') harmony = null;
  if (harmony && !HARMONIES.includes(harmony)) throw new Error(`unknown harmony ${harmony}`);
  return { colors, temperature, harmony };
}

function seedOf(s) {
  const n = Number(s);
  if (!Number.isSafeInteger(n)) throw new Error('seed must be an integer below 2^53');
  return n;
}

export async function staticApi(path) {
  const [p, qs] = path.split('?');
  const clean = p.replace(/^\/+/, '');
  const q = new URLSearchParams(qs || '');
  if (clean.startsWith('cli/')) {
    if (!qs) { try { return await file(clean); } catch { files.delete(clean); } }
    const seed = seedOf(clean.slice(4)), o = opts(q);
    const pal = generatePalettes(seed, o.harmony, o.colors, o.temperature);
    return { seed, colors: o.colors, temperature: o.temperature, source: 'javascript',
      palettes: Object.fromEntries(Object.entries(pal).map(([k, v]) => [k, withHls(v)])) };
  }
  if (clean === 'palette') {
    const o = opts(q), harmony = o.harmony || 'complementary', base = q.get('base');
    if (base) {
      const p = new PaletteGenerator(0).paletteFromBase(fromHex(base), harmony, o.colors, 'custom');
      return { ...withHls(p), seed: null, base, source: 'javascript' };
    }
    const seed = seedOf(q.get('seed') ?? 42);
    return { ...withHls(new PaletteGenerator(seed).generatePalette(o.temperature, harmony, o.colors)), seed, base: null, source: 'javascript' };
  }
  if (clean === 'png') throw new Error('The matplotlib PNG needs the local app (Python server).');
  return file(clean);
}
