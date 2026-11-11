// Pure JS port of the colour_palette package (color.py, generator.py) plus the parts of Python it relies on:
// random.seed / random.random / random.uniform (Mersenne Twister, CPython's seeding) and colorsys. The same seed gives
// the same palettes as `python colour_palette.py --seed N`. Tested against Python output in colour_engine.test.mjs.

export const HARMONIES = ['complementary', 'triadic', 'analogous', 'split_complementary', 'tetradic', 'monochromatic'];
export const TEMPERATURES = ['neutral', 'warm', 'cool'];

// Python float modulo: the result takes the sign of the divisor.
export function pyMod(x, y) {
  let m = x % y;
  if (m !== 0 && (y < 0) !== (m < 0)) m += y;
  else if (m === 0) m = y < 0 ? -0 : 0;
  return m;
}

// --- CPython's random module (MT19937, init_by_array seeding, 53-bit random()) ---------------------------------
export class PyRandom {
  constructor(seed = 0) { this.mt = new Uint32Array(624); this.seed(seed); }

  initGenrand(s) {
    const mt = this.mt;
    mt[0] = s >>> 0;
    for (let i = 1; i < 624; i++) {
      const prev = mt[i - 1] ^ (mt[i - 1] >>> 30);
      mt[i] = (Math.imul(1812433253, prev) + i) >>> 0;
    }
    this.mti = 624;
  }

  // random.seed(int): the 32-bit words of abs(seed), least significant first (seed must be a safe integer).
  seed(n) {
    let a = Math.abs(Math.trunc(Number(n)));
    if (!Number.isSafeInteger(a)) throw new Error('seed must be an integer below 2^53');
    const key = [];
    do { key.push(a % 4294967296); a = Math.floor(a / 4294967296); } while (a > 0);
    this.initGenrand(19650218);
    const mt = this.mt;
    let i = 1, j = 0;
    for (let k = Math.max(624, key.length); k; k--) {
      const prev = mt[i - 1] ^ (mt[i - 1] >>> 30);
      mt[i] = ((mt[i] ^ Math.imul(prev, 1664525)) + key[j] + j) >>> 0;
      i++; j++;
      if (i >= 624) { mt[0] = mt[623]; i = 1; }
      if (j >= key.length) j = 0;
    }
    for (let k = 623; k; k--) {
      const prev = mt[i - 1] ^ (mt[i - 1] >>> 30);
      mt[i] = ((mt[i] ^ Math.imul(prev, 1566083941)) - i) >>> 0;
      i++;
      if (i >= 624) { mt[0] = mt[623]; i = 1; }
    }
    mt[0] = 0x80000000;
    this.mti = 624;
  }

  uint32() {
    const mt = this.mt;
    if (this.mti >= 624) {
      for (let k = 0; k < 624; k++) {
        const y = (mt[k] & 0x80000000) | (mt[(k + 1) % 624] & 0x7fffffff);
        mt[k] = (mt[(k + 397) % 624] ^ (y >>> 1) ^ (y & 1 ? 0x9908b0df : 0)) >>> 0;
      }
      this.mti = 0;
    }
    let y = mt[this.mti++];
    y ^= y >>> 11;
    y ^= (y << 7) & 0x9d2c5680;
    y ^= (y << 15) & 0xefc60000;
    y ^= y >>> 18;
    return y >>> 0;
  }

  random() {
    const a = this.uint32() >>> 5, b = this.uint32() >>> 6;
    return (a * 67108864.0 + b) * (1.0 / 9007199254740992.0);
  }

  uniform(a, b) { return a + (b - a) * this.random(); }
}

// --- colorsys --------------------------------------------------------------------------------------------------
export function hsvToRgb(h, s, v) {
  if (s === 0.0) return [v, v, v];
  let i = Math.trunc(h * 6.0);
  const f = (h * 6.0) - i;
  const p = v * (1.0 - s), q = v * (1.0 - s * f), t = v * (1.0 - s * (1.0 - f));
  i = pyMod(i, 6);
  return [[v, t, p], [q, v, p], [p, v, t], [p, q, v], [t, p, v], [v, p, q]][i];
}

function hueOf(r, g, b, maxc, rangec) {
  const rc = (maxc - r) / rangec, gc = (maxc - g) / rangec, bc = (maxc - b) / rangec;
  let h;
  if (r === maxc) h = bc - gc;
  else if (g === maxc) h = 2.0 + rc - bc;
  else h = 4.0 + gc - rc;
  return pyMod(h / 6.0, 1.0);
}

export function rgbToHsv(r, g, b) {
  const maxc = Math.max(r, g, b), minc = Math.min(r, g, b), rangec = maxc - minc;
  if (minc === maxc) return [0.0, 0.0, maxc];
  return [hueOf(r, g, b, maxc, rangec), rangec / maxc, maxc];
}

// colorsys.rgb_to_hls: returns [h, l, s] (note the order, as in Python).
export function rgbToHls(r, g, b) {
  const maxc = Math.max(r, g, b), minc = Math.min(r, g, b), sumc = maxc + minc, rangec = maxc - minc;
  const l = sumc / 2.0;
  if (minc === maxc) return [0.0, l, 0.0];
  const s = l <= 0.5 ? rangec / sumc : rangec / (2.0 - maxc - minc);
  return [hueOf(r, g, b, maxc, rangec), l, s];
}

// --- color.py ----------------------------------------------------------------------------------------------------
// Color(h, s, v) with __post_init__: hue wrapped to [0, 1), saturation and value clamped to [0, 1].
export function color(h, s, v) {
  return { h: pyMod(h, 1.0), s: Math.max(0.0, Math.min(1.0, s)), v: Math.max(0.0, Math.min(1.0, v)) };
}
export const toRgb = c => hsvToRgb(c.h, c.s, c.v);
export const rgb255 = c => toRgb(c).map(x => Math.trunc(x * 255));
export const toHex = c => '#' + rgb255(c).map(x => x.toString(16).padStart(2, '0')).join('');
export function fromRgb(r, g, b) { const [h, s, v] = rgbToHsv(r, g, b); return color(h, s, v); }
export function fromHex(hex) {
  const m = /^#?([0-9a-f]{6})$/i.exec(String(hex).trim());
  if (!m) throw new Error(`not a #rrggbb colour: ${hex}`);
  const n = parseInt(m[1], 16);
  return fromRgb(((n >> 16) & 255) / 255, ((n >> 8) & 255) / 255, (n & 255) / 255);
}

// --- numpy helpers (np.mean uses pairwise summation: 8 partial sums for 8..128 items) ---------------------------
export function npSum(a) {
  const n = a.length;
  if (n < 8) { let s = -0.0; for (const x of a) s += x; return n ? s : 0; }
  if (n > 128) { const m = Math.floor(n / 2 / 8) * 8; return npSum(a.slice(0, m)) + npSum(a.slice(m)); }
  const r = a.slice(0, 8);
  let i = 8;
  for (; i < n - (n % 8); i += 8) for (let k = 0; k < 8; k++) r[k] += a[i + k];
  let res = ((r[0] + r[1]) + (r[2] + r[3])) + ((r[4] + r[5]) + (r[6] + r[7]));
  for (; i < n; i++) res += a[i];
  return res;
}
export const npMean = a => npSum(a) / a.length;

// Python >= 3.12 builtin sum() of floats (start 0): Neumaier compensated summation (bltinmodule.c).
export function pySum(a) {
  if (!a.length) return 0;
  let f = 0 + a[0], c = 0.0;
  for (let i = 1; i < a.length; i++) {
    const x = a[i], t = f + x;
    if (Math.abs(f) >= Math.abs(x)) c += (f - t) + x; else c += (x - t) + f;
    f = t;
  }
  return c && Number.isFinite(c) ? f + c : f;
}
const clip01 = x => Math.min(Math.max(x, 0), 1);

// --- generator.py ------------------------------------------------------------------------------------------------
export class PaletteGenerator {
  constructor(seed = null) { this.rand = new PyRandom(seed ?? Math.floor(Math.random() * 2 ** 32)); }

  generateBaseColor(temperature = 'neutral') {
    const R = this.rand;
    let h;
    if (temperature === 'warm') h = pyMod(R.uniform(0.95, 1.15), 1.0);
    else if (temperature === 'cool') h = R.uniform(0.45, 0.65);
    else h = R.random();
    const s = R.uniform(0.6, 0.9);
    const v = R.uniform(0.7, 0.9);
    return color(h, s, v);
  }

  adjustColor(c, hueShift = 0.0, satAdjust = 0.0, valAdjust = 0.0) {
    return color(pyMod(c.h + hueShift, 1.0), clip01(c.s + satAdjust), clip01(c.v + valAdjust));
  }

  generateHarmony(base, harmony, numColors = 5) {
    if (!(numColors >= 1)) throw new Error(`num_colors must be at least 1, got ${numColors}`);
    if (!HARMONIES.includes(harmony)) throw new Error(`unknown harmony ${harmony}`);
    const colors = [base], adj = (...a) => this.adjustColor(base, ...a);
    if (harmony === 'complementary') colors.push(adj(0.5));
    else if (harmony === 'triadic') colors.push(adj(1 / 3), adj(2 / 3));
    else if (harmony === 'analogous') for (let i = 1; i < numColors; i++) colors.push(adj(0.05 * i));
    else if (harmony === 'split_complementary') {
      const comp = pyMod(base.h + 0.5, 1.0);
      colors.push(color(comp - 0.05, base.s, base.v), color(comp + 0.05, base.s, base.v));
    } else if (harmony === 'tetradic') colors.push(adj(0.25), adj(0.5), adj(0.75));
    else for (let i = 1; i < numColors; i++) colors.push(adj(0.0, -0.15 * i, 0.1 * i));
    return colors.slice(0, numColors);
  }

  analyzePalette(colors) {
    const rgbs = colors.map(toRgb);
    const bright = rgbs.map(rgb => pySum(rgb) / 3);
    const brightness = npMean(bright);
    const warmth = npMean(rgbs.map(([r, , b]) => r - b));
    const contrast = Math.max(...bright) - Math.min(...bright);
    return { brightness, temperature: warmth > 0 ? 'warm' : 'cool', contrast, harmony_level: Math.min(1.0, contrast * 2) };
  }

  paletteFromBase(base, harmony = 'complementary', numColors = 5, temperature = 'neutral') {
    const colors = this.generateHarmony(base, harmony, numColors);
    return {
      colors: colors.map(toHex), rgb_values: colors.map(rgb255), hsv_values: colors.map(c => [c.h, c.s, c.v]),
      analysis: this.analyzePalette(colors), harmony_type: harmony, temperature,
    };
  }

  generatePalette(temperature = 'neutral', harmony = 'complementary', numColors = 5) {
    return this.paletteFromBase(this.generateBaseColor(temperature), harmony, numColors, temperature);
  }
}

// generator.generate_palettes: one CLI run (all harmonies in order from one seeded generator, or just one).
export function generatePalettes(seed = null, harmony = null, numColors = 5, temperature = 'neutral') {
  const g = new PaletteGenerator(seed);
  const out = {};
  for (const h of harmony ? [harmony] : HARMONIES) out[h] = g.generatePalette(temperature, h, numColors);
  return out;
}

// Palette for a chosen base colour (hex): ColorPaletteGenerator().palette_from_base(Color.from_rgb(...)).
export function paletteFromHex(hex, harmony, numColors = 5) {
  return new PaletteGenerator(0).paletteFromBase(fromHex(hex), harmony, numColors, 'custom');
}

// visualizer.gradient_blend: width RGB triples blending through the colours (one row; the PNG uses two identical rows).
export function gradientBlend(colors, width = 256) {
  const rgbs = colors.map(toRgb), out = new Array(width);
  if (rgbs.length === 1) return out.fill(rgbs[0]);
  const nSeg = rgbs.length - 1;
  for (let i = 0; i < nSeg; i++) {
    const a = Math.floor(i * width / nSeg), b = Math.floor((i + 1) * width / nSeg), L = b - a;
    // np.linspace(start, end, L): start + j * ((end - start) / (L - 1)), with the last point set to end exactly
    for (let j = 0; j < L; j++) {
      out[a + j] = j === L - 1 && L > 1 ? rgbs[i + 1].slice()
        : rgbs[i].map((x, k) => x + j * ((rgbs[i + 1][k] - x) / (L - 1)));
    }
  }
  return out;
}
