# Coursekin browser edition

[Study with Coursekin](https://coursekin.alx21.chatgpt.site). Create a class, add course materials and ask questions grounded in relevant source excerpts. No paid AI API, account or API key is needed.

The first run downloads model files from public hosts. Text generation runs in a dedicated browser worker using WebLLM; prompts are not sent to a hosted model. The default is Qwen 3 1.7B, with larger Qwen 3 4B and smaller Llama 3.2 1B choices. Model downloads are cached when browser storage permits.

Use HTTPS (or localhost) and a current browser with WebGPU and compatible graphics hardware. A model choice does not guarantee that every device has enough memory. Download speed, inference speed and answer quality depend on the device and model. Stop a download or generation from the interface; errors preserve existing inputs. There is no paid model fallback. Hosting and model-download bandwidth remain separate from AI API fees.

## Study space

Classes, extracted text and conversation are stored in IndexedDB on this device. Upload PDF, DOCX, TXT or Markdown, up to 25 MB per file, 600,000 extracted characters per document and 20 documents per class. PDFs are capped at 1,500 pages; scanned files require OCR first. Files are read in the browser and are not uploaded to a server.

Coursekin ranks overlapping text chunks by question terms and supplies up to six relevant excerpts to the browser model. The answer must cite known excerpt IDs. Open each citation to read the actual passage and page. Citation validation checks identifiers, not whether every statement is entailed. No matching passages produces a visible request to narrow the question or add material.

Export a class backup to keep documents and conversation or move them to another device. Import creates a new class rather than overwriting an existing one. Browser data can be lost when cleared or evicted. Remove documents or delete a class from the study space.

## Local preview and hosting

This source checkout is a static website. Serve `dist/` on localhost, for example `python -m http.server 8000 --directory dist`. No server model, environment variable or build dependency is required. `dist/app.mjs` handles class storage, extraction, retrieval and local generation. Document readers and model assets use pinned public CDN URLs. `.openai/hosting.json` retains this site's identity.

The separate earlier Python desktop application and host plugin are separate editions. This source implements the no-paid-API website; it does not claim those earlier editions have been converted or their packaged releases rebuilt.

## Privacy and limitations

Materials, questions and responses stay on this device. Public model and reader asset hosts and the website host may receive ordinary request metadata. Answers can be wrong; check source excerpts and class rules. Lexical retrieval can miss relevant passages when wording differs. Browser inference requires compatible graphics hardware and sufficient memory.

## License

Site code retains its existing licensing; model weights and third-party libraries retain their respective licenses.
