import { build } from 'esbuild';
import { readFileSync, readdirSync, mkdirSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = fileURLToPath(new URL('.', import.meta.url));
const assets = {}, types = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8', '.svg': 'image/svg+xml', '.png': 'image/png' };
const files = ['index.html', 'style.css', 'favicon.svg', 'coursekin-desktop.png', 'app.mjs', 'browser-model.mjs', 'browser-model-worker.mjs', 'answer-contract.mjs', 'hosted-answer.mjs'];
// Pure study data helpers are browser modules, not server code or build inputs.
if (readdirSync(root).includes('study-data.mjs')) files.push('study-data.mjs');
for (const file of files) assets[file === 'index.html' ? '/' : '/' + file] = { type: types[path.extname(file)], data: readFileSync(path.join(root, file)).toString('base64') };
await build({ absWorkingDir: root, entryPoints: ['worker.mjs'], outfile: 'dist/server/index.js', bundle: true, format: 'esm', platform: 'browser', target: 'es2022', minify: true,
  plugins: [{ name: 'coursekin-assets', setup(builder) {
    builder.onResolve({ filter: /^coursekin:assets$/ }, () => ({ path: 'assets', namespace: 'coursekin' }));
    builder.onLoad({ filter: /.*/, namespace: 'coursekin' }, () => ({ contents: `export default ${JSON.stringify(assets)}`, loader: 'js' }));
  } }],
});
mkdirSync(path.join(root, 'dist/.openai'), { recursive: true });
writeFileSync(path.join(root, 'dist/.openai/hosting.json'), readFileSync(path.join(root, '.openai/hosting.json')));
console.log('Built the Coursekin Worker and explicit browser assets.');
