# Coursekin browser edition

[Study with Coursekin](https://coursekin.alx21.chatgpt.site). Create a class, add course materials and ask questions with source excerpts you can inspect.

## Choose where answers run

**On this device** uses the experimental Qwen 3 4B browser model. It needs no account, API key or paid model service. The first use downloads model assets from public hosts. Use HTTPS or localhost, a WebGPU browser, compatible graphics hardware and sufficient memory/storage. Downloads are cached when browser storage permits. Stop cancels generation; the next question reloads the cached model.

**OpenAI with your key** uses your own OpenAI API account and billing, with GPT-5.4 as the default and GPT-5.4 mini as an option. Enter a key in the masked field, then ask a question. There is no publisher-funded key or automatic switch to a paid service. The key stays in tab memory; **Clear key**, switching to device mode, leaving the page or reloading clears it. Backups exclude it.

For hosted answers, your question, up to six selected source excerpts with filenames/page numbers and the last four conversation messages pass through the Coursekin server to OpenAI. Original file binaries are not uploaded. Requests use `store: false`; provider data policies still apply. Citation checks validate source identifiers, not whether every claim is supported or the reasoning is correct. Review the answer and open its sources in either mode.

The smaller browser models were removed after a real Qwen 1.7B test added three scores and returned 240% for a weighted-grade question whose answer was 78%. Qwen 4B gave the correct calculation on that example; this does not establish general reliability or support on other hardware.

## Study space

1. Name a class and add readable PDF, DOCX, TXT or Markdown materials.
2. Choose a mode. Device mode downloads its model; hosted mode requires your own key.
3. Ask a question using terms from your materials, then open the cited excerpts.
4. Export a class backup before clearing browser data or changing devices.

Each file may be up to 25 MB, with 600,000 extracted characters and at most 1,500 PDF pages. A class accepts up to 20 documents. Scanned PDFs need OCR first. Diagrams, tables and complex equations may not survive text extraction.

Classes, extracted text and conversations are saved in IndexedDB in this browser profile. Original uploaded binaries are not kept in backups. A backup import creates a new class instead of replacing existing work. Keep backups private; they are not encrypted. Browser storage cleanup or eviction can remove classes. Classes do not sync between devices or with the Python app or plugin.

Retrieval ranks overlapping text chunks by question terms and supplies up to six excerpts. It supports Unicode and short terms such as pH, but keyword matching can still miss relevant passages or broader context. No matching passage produces a request to narrow the question or add material. An excerpt ID does not prove an answer is true.

## Development and preview

For **device-only** preview, run this from the repository root:

```sh
python -m http.server 8000 --bind 127.0.0.1 --directory web
```

Open `http://127.0.0.1:8000`. A static server does not provide hosted answers.

For the full browser app, use Node.js 22 or newer:

```sh
cd web
npm ci
npm test
npm run build
npm run preview
```

Open `http://127.0.0.1:5177`. The preview runs the built Cloudflare Worker, including `POST /api/answer/visitor`. Supply a visitor key through the browser field only; no server environment key is needed. From the repository root, `node --test tests/browser-data.test.mjs web/test/*.test.mjs` also covers backup validation and retrieval.

`build.mjs` embeds an explicit browser-asset allowlist into `dist/server/index.js`. It excludes server source, configuration, environment files and dependencies from public asset routes. `.openai/hosting.json` identifies the existing Site. Preserve its project ID. The Python app serves `local-web/`; keep its entry point separate from this edition.

## Verification and limits

Deterministic tests cover source references, malformed backups, Unicode retrieval, request bounds, credential exclusion, provider errors, rejected redirects and cancellation of a stalled upload. Provider responses in those tests are synthetic; they do not measure answer quality. Real browser and provider observations are recorded in the repository's [verification guide](https://github.com/agammann/coursekin/blob/main/docs/verification.md).

Use Coursekin to support your study process. Check source excerpts and follow your class rules. Model output can still omit facts, misunderstand a passage or make a calculation error.

## License

Coursekin code is MIT licensed. Model weights and third-party libraries retain their respective licenses.
