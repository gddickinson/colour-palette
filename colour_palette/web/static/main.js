// Entry point: registers the lazily loaded pages, sets the footer mode text and starts the router.
import { start, route, lazy, app, isStatic, $ } from './core.js';

const PAGES = {
  'home.js': ['home'], 'generate.js': ['generate'], 'harmonies.js': ['harmonies'], 'check.js': ['check'], 'about.js': ['about'],
};
lazy(Object.fromEntries(Object.entries(PAGES).flatMap(([file, names]) => names.map(n => [n, () => import('./' + file)]))));

route('notfound', () => { app().innerHTML = '<h1>Not found</h1><p><a href="#/">Back to the start</a></p>'; });

$('#mode').textContent = isStatic()
  ? 'static site: palettes are generated in your browser (JS port of the Python generator, same seeds, same colours)'
  : 'local app: palettes come from the Python package on this machine';
start();
