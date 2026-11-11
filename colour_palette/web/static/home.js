// Home page: hero with the default CLI run (seed 42) as six strips, counts from the API, entry cards.
import { route, api, app, esc, list } from './core.js';
import { generatePalettes } from './colour_engine.js';
import { setInfo, harmonyName } from './ui.js';

const DOORS = [
  ['#/generate', 'Generator', 'Seeded or hand-picked base colour, any harmony, 1-24 colours; hex, RGB, HSV and HSL with copy buttons; JSON, PNG and CSS export.'],
  ['#/harmonies', 'Harmonies', 'The six colour-theory rules on a hue wheel, with the exact hue and saturation steps the generator uses.'],
  ['#/check', 'Cross-check', 'The browser engine against the Python package: the same seeds, compared colour by colour and number by number.'],
  ['#/about', 'About', 'How palettes are made and analysed, how to run the command-line tool and the web app, credits.'],
];

route('home', async () => {
  const info = await api('/info');
  setInfo(info);
  const run = generatePalettes(42, null, 5);
  app().innerHTML = `
  <section class="hero two herogrid">
    <div>
      <p class="kicker">Colour theory · six harmonies · reproducible seeds</p>
      <h1 class="glow">Colour Palette Generator</h1>
      <p class="lead">${esc(info.description)} Pick a seed or a base colour and get complementary, triadic, analogous,
      split-complementary, tetradic and monochromatic palettes, with their brightness, temperature and contrast.
      The generator also runs entirely in your browser: it is ported from the Python package and tested against it.</p>
      <a class="btn" href="#/generate">Open the generator</a><a class="btn alt" href="#/harmonies">See the harmonies</a>
    </div>
    <div class="strips" aria-label="The default command-line run, seed 42">
      ${list(Object.entries(run), ([k, p]) => `<a href="#/generate?seed=42&h=all&n=5&t=neutral">
        <span>${esc(harmonyName(k))}</span><span class="bar" role="img" aria-label="${esc(harmonyName(k))}: ${p.colors.join(' ')}">${list(p.colors, c => `<span style="background:${c}"></span>`)}</span></a>`)}
      <p class="small mute">The default run, <code>python colour_palette.py</code> (seed 42): the palettes in the repo's palette_*.png.</p>
    </div>
  </section>
  <div class="tiles">
    <div class="tile"><b>${info.harmonies.length}</b><span>harmony types</span></div>
    <div class="tile"><b>${info.temperatures.length}</b><span>temperature preferences</span></div>
    <div class="tile"><b>4</b><span>notations: hex, RGB, HSV, HSL</span></div>
    <div class="tile"><b>${info.max_colors}</b><span>colours per palette (web limit)</span></div>
  </div>
  <div class="grid wide">${list(DOORS, ([href, t, d]) => `<a class="card door" href="${href}"><b>${t}</b><span>${d}</span></a>`)}</div>
  <h2>Harmony types</h2>
  <p>${list(info.harmonies, h => `<a class="tag a" href="#/generate?seed=42&h=${h.id}&n=5&t=neutral">${esc(h.name)}</a>`)}</p>`;
});
