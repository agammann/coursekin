# Third-party notices

Coursekin code and original assets use the [MIT license](LICENSE). These components retain their own licenses. Uploaded textbooks and course materials are not relicensed.

| Component | Use | License/source |
| :--- | :--- | :--- |
| Qwen3-4B | Optional browser model weights | Apache-2.0; [Qwen model](https://huggingface.co/Qwen/Qwen3-4B), [MLC weights](https://huggingface.co/mlc-ai/Qwen3-4B-q4f16_1-MLC) |
| WebLLM 0.2.85 and MLC runtime | Optional WebGPU inference | Apache-2.0; [WebLLM](https://github.com/mlc-ai/web-llm), [MLC LLM](https://github.com/mlc-ai/mlc-llm) |
| PDF.js 6.4.299 | Browser PDF extraction | Apache-2.0; [PDF.js](https://github.com/mozilla/pdf.js) |
| fflate 0.8.3 | Browser DOCX ZIP extraction | MIT; [fflate](https://github.com/101arrowz/fflate) |
| pypdf 6.10.0 | Python PDF extraction | BSD-3-Clause; [pypdf](https://github.com/py-pdf/pypdf) |
| psutil 7.2.2 | macOS parser memory checks | BSD-3-Clause; [psutil](https://github.com/giampaolo/psutil) |
| Playwright 1.62.1 | Browser verification | Apache-2.0; [Playwright](https://github.com/microsoft/playwright) |
| esbuild 0.28.1 | Browser build | MIT; [esbuild](https://github.com/evanw/esbuild) |
| Wrangler 4.146.0 and Miniflare | Worker preview/build tooling | Apache-2.0/MIT; [Cloudflare workers SDK](https://github.com/cloudflare/workers-sdk) |

The browser downloads model/runtime and document-reader assets from the pinned public hosts in `web/`. Those libraries and weights are not included in the source ZIP. Development versions are in `web/package-lock.json`; installed packages include upstream licenses. Hosted answers use a service selected by the user; no hosted model weights or publisher key are redistributed.
