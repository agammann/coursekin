import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const base = process.env.COURSEKIN_TEST_URL || 'http://127.0.0.1:5177';
const out = path.join(ROOT, 'web/outputs');
await fs.mkdir(out, { recursive: true });
const checks = [], errors = [], requests = [];
let mode = 'valid', posts = 0;
const browser = await chromium.launch({ executablePath: process.env.COURSEKIN_TEST_EXECUTABLE || undefined, headless: process.env.COURSEKIN_TEST_HEADLESS !== '0' });
const context = await browser.newContext({ acceptDownloads: true, viewport: { width: 1440, height: 1000 } });
const page = await context.newPage();
const pdfWorkers = [];
page.on('worker', worker => {
    // This fixture does not load a model. PDF.js owns the page workers,
    // including blob wrappers used for its cross-origin worker module.
    const record = { url: worker.url(), closed: false };
    pdfWorkers.push(record);
    worker.on('close', () => { record.closed = true; });
});
page.on('pageerror', e => errors.push(e.message));
page.on('request', r => { if (r.method() === 'POST')
    requests.push({ url: r.url(), method: r.method() }); });
function ok(name, value) { assert.ok(value, name); checks.push(name); }
async function state() { return page.evaluate(() => new Promise((resolve, reject) => { const r = indexedDB.open('coursekin-browser', 1); r.onsuccess = () => { const d = r.result, q = d.transaction('classes').objectStore('classes').getAll(); q.onsuccess = () => { resolve(q.result); d.close(); }; q.onerror = () => reject(q.error); }; r.onerror = () => reject(r.error); })); }
async function ask(question) { await page.locator('#question').fill(question); await page.locator('#ask').click(); await page.locator('#ask').waitFor({ state: 'visible' }); await page.waitForFunction(() => !document.getElementById('ask').disabled); }
try {
    await page.route('**/api/answer/visitor', async (route) => { posts++; const input = route.request().postDataJSON().question; if (mode === 'slow') {
        await new Promise(r => setTimeout(r, 3000));
        try {
            await route.fulfill({ status: 503, json: { error: 'fixture delayed' } });
        }
        catch { }
        ;
        return;
    } if (mode === 'invalid') {
        await route.fulfill({ json: { model: 'gpt-5.4', value: { answer: 'A fabricated answer [source:99]', sourceIds: ['99'] } } });
        return;
    } const source = input.excerpts.find(s => s.text.includes('40 percent')) || input.excerpts[0]; await route.fulfill({ json: { model: 'gpt-5.4', value: { answer: `The final exam is worth 40 percent [source:${source.id}].`, sourceIds: [source.id] } } }); });
    await page.goto(base);
    await page.locator('#class-name').fill('Biology 101 practice');
    await page.locator('#class-form button').click();
    await page.waitForFunction(() => document.querySelector('#class-select').options.length === 1);
    ok('class saved', (await state())[0].name === 'Biology 101 practice');
    await page.locator('#materials').setInputFiles([path.join(ROOT, 'examples/biology-textbook.txt'), path.join(ROOT, 'examples/practice-syllabus.md'), path.join(out, 'fixtures/practice-textbook.docx'), path.join(out, 'fixtures/practice-syllabus.pdf')]);
    await page.waitForFunction(() => !document.querySelector('#materials').disabled);
    const courses = await state();
    ok('TXT Markdown DOCX PDF parsed locally', courses[0].documents.length === 4);
    ok('PDF extracted weight and date', courses[0].documents.find(d => d.name.endsWith('.pdf')).pages[0].includes('June 11'));
    ok('DOCX extracted textbook', courses[0].documents.find(d => d.name.endsWith('.docx')).pages[0].includes('thylakoid'));
    await page.waitForFunction(() => !document.querySelector('#materials').disabled);
    ok('PDF extraction closes its worker', pdfWorkers.length > 0 && pdfWorkers.every(worker => worker.closed));
    ok('no upload POST during import', posts === 0);
    await page.locator('[name="answer-mode"][value="hosted"]').check();
    const fakeKey = 'sk-' + 'fixture'.repeat(6);
    await page.locator('#hosted-key').fill(fakeKey);
    await ask('What percent of the grading is the final exam?');
    ok('valid fixture answer rendered', await page.locator('#conversation').innerText().then(t => t.includes('40 percent')));
    await page.locator('#conversation details').first().evaluate(e => e.open = true);
    ok('citation opens exact imported text', await page.locator('#conversation details pre').first().innerText().then(t => t.includes('40 percent')));
    const before = (await state())[0];
    ok('successful answer saved', before.messages.length === 2);
    mode = 'invalid';
    await ask('What percent is the final exam worth?');
    ok('invalid source reference rejected', await page.locator('#study-error').innerText().then(t => t.includes('valid source references')));
    ok('invalid response preserves conversation', (await state())[0].messages.length === 2);
    mode = 'slow';
    await page.locator('#question').fill('What percent is the final exam worth?');
    await page.locator('#ask').click();
    await page.locator('#stop-answer').click();
    await page.waitForFunction(() => !document.querySelector('#ask').disabled);
    ok('cancel keeps question', await page.locator('#question').inputValue() === 'What percent is the final exam worth?');
    ok('cancel preserves saved conversation', (await state())[0].messages.length === 2);
    const count = posts;
    await ask('xyznotfound');
    ok('missing passage stops before provider', posts === count);
    ok('missing passage gives useful message', await page.locator('#study-error').innerText().then(t => t.includes('No matching passages')));
    // Abort one genuine IndexedDB write. This simulates quota/storage failure,
    // while retaining the app's real UI, transaction and export behavior.
    await page.evaluate(() => { const original = IDBObjectStore.prototype.put; IDBObjectStore.prototype.put = function (...args) { const result = original.apply(this, args); this.transaction.abort(); IDBObjectStore.prototype.put = original; return result; }; });
    mode = 'valid';
    await ask('What percent is the final exam worth?');
    ok('aborted transaction leaves saved messages unchanged', (await state())[0].messages.length === 2);
    const downloadPromise = page.waitForEvent('download');
    await page.locator('#backup').click();
    const download = await downloadPromise;
    await download.saveAs(path.join(out, 'class.json'));
    const backup = JSON.parse(await fs.readFile(path.join(out, 'class.json'), 'utf8'));
    ok('storage failure also leaves exported conversation unchanged', backup.messages.length === 2);
    ok('backup excludes key', !JSON.stringify(backup).includes(fakeKey));
    await page.locator('#restore').setInputFiles(path.join(out, 'class.json'));
    await page.waitForFunction(() => document.querySelector('#class-select').options.length === 2);
    ok('restore creates new class', (await state()).length === 2);
    ok('restore retains exact text and citation excerpts', JSON.stringify((await state())[1].documents) === JSON.stringify(before.documents));
    await page.locator('#restore').setInputFiles(path.join(out, 'fixtures/bad-backup.json'));
    await page.waitForFunction(() => !document.querySelector('#restore').disabled);
    ok('invalid backup preserves classes', (await state()).length === 2);
    ok('invalid backup explained', await page.locator('#study-error').innerText().then(t => t.includes('not a supported')));
    await page.evaluate(() => {
        const original = IDBObjectStore.prototype.delete;
        IDBObjectStore.prototype.delete = function (...args) {
            const result = original.apply(this, args);
            this.transaction.abort();
            IDBObjectStore.prototype.delete = original;
            return result;
        };
    });
    page.once('dialog', d => d.accept());
    await page.locator('#delete-class').click();
    await page.waitForFunction(() => document.querySelector('#study-error').textContent.includes('Browser storage could not save'));
    ok('failed deletion keeps both classes', (await state()).length === 2);
    ok('failed deletion explains storage failure', await page.locator('#study-error').innerText().then(t => t.includes('saved class is unchanged')));
    page.once('dialog', d => d.accept());
    await page.locator('#delete-class').click();
    await page.waitForFunction(() => document.querySelector('#class-select').options.length === 1);
    ok('delete removes only selected class', (await state()).length === 1);
    await page.reload();
    await page.waitForFunction(() => document.querySelector('#class-select').options.length === 1);
    ok('reload retains class and conversation', (await state())[0].messages.length === 2);
    ok('reload clears API key', await page.locator('#hosted-key').inputValue() === '');
    ok('reload returns to device mode', await page.locator('[value="device"]').isChecked());
    await page.locator('[value="hosted"]').check();
    await page.locator('#hosted-key').fill(fakeKey);
    await page.locator('[value="device"]').check();
    ok('switch to device clears key', await page.locator('#hosted-key').inputValue() === '');
    await page.locator('#materials').setInputFiles(path.join(out, 'fixtures/unreadable.pdf'));
    await page.waitForFunction(() => !document.querySelector('#materials').disabled);
    ok('unreadable file preserves materials', (await state())[0].documents.length === 4);
    ok('unreadable file shows error', (await page.locator('#study-error').innerText()).length > 0);
    ok('malformed PDF closes its worker', pdfWorkers.every(worker => worker.closed));
    await page.locator('#materials').setInputFiles(path.join(out, 'fixtures/practice-syllabus.pdf'));
    await page.waitForFunction(() => !document.querySelector('#materials').disabled);
    ok('valid PDF import works after malformed load', (await state())[0].documents.length === 5);
    ok('recovered PDF import closes its worker', pdfWorkers.every(worker => worker.closed));
    for (const width of [1440, 390, 320]) {
        await page.setViewportSize({ width, height: 1000 });
        await page.screenshot({ path: path.join(out, `viewport-${width}.png`), fullPage: true });
        ok(`viewport ${width} has no horizontal overflow`, await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    }
    ok('no unexpected page errors', errors.length === 0);
}
catch (error) {
    errors.push(error.stack);
    throw error;
}
finally {
    await fs.writeFile(path.join(out, 'verification.json'), JSON.stringify({ url: base, browser: browser.version(), checks, errors, requests, pdfWorkers, providerBoundary: 'synthetic responses; actual UI/storage/parser/recovery', status: errors.length ? 'failed' : 'passed' }, null, 2));
    await browser.close();
}
