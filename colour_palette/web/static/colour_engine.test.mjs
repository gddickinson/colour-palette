// Node test: colour_engine.js reproduces the Python package (random, colorsys, color.py, generator.py, visualizer.py).
// Reference values: tests/fixtures/colour_engine.json, written by `python scripts/make_engine_fixture.py --write`;
// tests/test_web.py checks the fixture is current. Run: node colour_palette/web/static/colour_engine.test.mjs
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import {
  PyRandom, PaletteGenerator, color, toHex, toRgb, rgbToHsv, rgbToHls, fromHex, generatePalettes, gradientBlend,
} from './colour_engine.js';

const FIX = JSON.parse(readFileSync(new URL('../../../tests/fixtures/colour_engine.json', import.meta.url)));
let n = 0, exactFloats = 0, floats = 0;
const close = (a, b, what, tol = 1e-12) => {
  floats++; if (a === b) exactFloats++;
  assert.ok(Math.abs(a - b) <= tol * Math.max(1, Math.abs(b)), `${what}: js ${a} vs py ${b}`);
};
const closeArr = (a, b, what) => { assert.equal(a.length, b.length, what + ' length'); a.forEach((x, i) => close(x, b[i], `${what}[${i}]`)); };

function samePalette(js, py, what) {
  assert.deepEqual(js.colors, py.colors, what + ' hex');
  assert.deepEqual(js.rgb_values, py.rgb_values, what + ' rgb');
  js.hsv_values.forEach((h, i) => closeArr(h, py.hsv_values[i], `${what} hsv ${i}`));
  for (const k of ['brightness', 'contrast', 'harmony_level']) close(js.analysis[k], py.analysis[k], `${what} ${k}`);
  assert.equal(js.analysis.temperature, py.analysis.temperature, what + ' temperature');
  assert.equal(js.harmony_type, py.harmony_type); n++;
}

// 1. Mersenne Twister with CPython's seeding: random() and uniform()
for (const c of FIX.mt) {
  const r = new PyRandom(c.seed);
  c.random.forEach((v, i) => assert.equal(r.random(), v, `seed ${c.seed} random #${i}`));
  c.uniform.forEach((v, i) => assert.equal(r.uniform(0.6, 0.9), v, `seed ${c.seed} uniform #${i}`));
  n++;
}
// 2. colour-space conversions: Color(h,s,v) wrapping/clamping, to_rgb, to_hex, rgb_to_hsv, rgb_to_hls, hex -> HSV
for (const [h, s, v, ph, ps, pv, hex, rgb] of FIX.conversions.color) {
  const c = color(h, s, v);
  closeArr([c.h, c.s, c.v], [ph, ps, pv], `Color(${h},${s},${v})`);
  assert.equal(toHex(c), hex); closeArr(toRgb(c), rgb, `to_rgb(${h},${s},${v})`); n++;
}
for (const [r, g, b, ...hsv] of FIX.conversions.rgb_to_hsv) { closeArr(rgbToHsv(r, g, b), hsv, `rgb_to_hsv(${r},${g},${b})`); n++; }
for (const [r, g, b, ...hls] of FIX.conversions.rgb_to_hls) { closeArr(rgbToHls(r, g, b), hls, `rgb_to_hls(${r},${g},${b})`); n++; }
for (const [hex, ...hsv] of FIX.conversions.hex_to_hsv) { const c = fromHex(hex); closeArr([c.h, c.s, c.v], hsv, hex); n++; }
// 3. every harmony for fixed base colours and several palette sizes (palette_from_base)
const g0 = new PaletteGenerator(0);
for (const c of FIX.harmonies) samePalette(g0.paletteFromBase(color(...c.base), c.harmony, c.n), c.palette, `${c.harmony} n=${c.n} base ${c.base}`);
// 4. seeded generate_palette for each temperature
for (const c of FIX.palettes) {
  samePalette(new PaletteGenerator(c.seed).generatePalette(c.temperature, c.harmony, c.n), c.palette, `seed ${c.seed} ${c.temperature} ${c.harmony}`);
}
// 5. whole CLI runs (generate_palettes): all six harmonies from one seeded generator
for (const c of FIX.cli) {
  const js = generatePalettes(c.seed, null, c.n);
  assert.deepEqual(Object.keys(js), Object.keys(c.palettes));
  for (const k of Object.keys(js)) samePalette(js[k], c.palettes[k], `cli seed ${c.seed} n=${c.n} ${k}`);
}
// 6. the PNG gradient strip (visualizer.gradient_blend)
for (const c of FIX.gradients) {
  const g = gradientBlend(c.bases.map(b => color(...b)));
  for (const [j, rgb] of Object.entries(c.cols)) closeArr(g[+j], rgb, `gradient n=${c.bases.length} col ${j}`);
  n++;
}
// 7. input checks
assert.throws(() => g0.generateHarmony(color(0.1, 0.5, 0.5), 'triadic', 0));
assert.throws(() => fromHex('#12345'));

console.log(`colour_engine: ${n} checks passed (${floats} floats, ${exactFloats} bit-identical to Python)`);
