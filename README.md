# Coursekin

Name your class. Add your textbook and syllabus. Ask away.

Coursekin has two editions: a local study app and a plugin skill for ChatGPT or Codex. They share tutoring guidance but use different storage and interfaces.

[Use the OpenAI plugin](https://chatgpt.com/plugins/plugins_6aaa22656ccc8191902ee998a70c8a86) · [Download the local app](https://github.com/agammann/coursekin/releases) · [Report a problem](https://github.com/agammann/coursekin/issues) · [MIT license](LICENSE)

![Coursekin local app](docs/coursekin-desktop.png)

## Local app

Install Python 3.12 or newer from [python.org](https://www.python.org/downloads/).

On Windows, double click **Start Coursekin.cmd**. On macOS or Linux, run `sh start.sh`. The launcher creates a virtual environment and installs the pinned dependencies on first use. It opens Coursekin at `http://127.0.0.1:8767`.

On first launch, paste your own OpenAI API key into the private terminal prompt. The key is hidden while you type. It is saved in `.env.local`, which is excluded from Git and release archives. API usage uses your own OpenAI billing. The plugin edition does not require a separate key.

The automated tests and package builds pass on Windows, macOS and Linux in [GitHub Actions](https://github.com/agammann/coursekin/actions). Interactive development and browser verification were performed on Windows; the other two launchers have not been exercised interactively on those operating systems.

For a manual setup:

```sh
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python setup_key.py
python launch.py
```

Then enter a class name, upload or paste a textbook and syllabus, and start asking questions. The interface supports keyboard navigation, file browsing, file dropping and pasted text. Source buttons open the extracted passage behind an answer. Your class list and conversations persist when you restart.

**Course materials** lets you add another document, export your extracted text and conversation as JSON, or delete a class. Export is a readable backup; importing a previous class export is not implemented.

### Supported material

| Format | Support |
| :--- | :--- |
| PDF | Searchable text, with references to PDF file page order |
| DOCX | Main document paragraphs, with paragraph locations |
| TXT and Markdown | UTF 8 text, with line locations |
| Pasted text | Stored as a text document |

Each file is limited to 30 MB. Each class supports up to 20 documents. PDFs are limited to 2,000 pages and 8 million extracted characters per document. Complex files may hit the memory or time limits sooner. Scanned PDFs need OCR before import. Diagrams, equations, tables and DOCX headers or comments may not be preserved. References identify retrieved excerpts, not a guarantee that every claim in a model answer is correct.

Coursekin uses local SQLite full text search to select passages. It does not send an entire textbook on every question. Broad summaries and questions whose wording differs substantially from the source can miss relevant sections; ask about a specific topic or add a relevant excerpt when needed.

### Storage and model

The local app stores extracted text and conversations in `data/coursekin.sqlite3`. It does not retain the uploaded file binary. Keep the original textbook and syllabus separately. Exports contain the extracted source text and should be treated as private.

Questions, recent conversation and selected excerpts go directly from the local server to OpenAI's Responses API. Requests set `store: false`; provider data handling still follows the [OpenAI API data policy](https://platform.openai.com/docs/guides/your-data). This is a local app using an online model, not an offline model.

The default model is `gpt-4.1-mini`. To change it, set `OPENAI_MODEL` in your server environment or `.env.local`. API keys are never returned by an app endpoint, embedded in the frontend, or placed in an export.

The server binds only to `127.0.0.1`. It is designed for one person on their own computer. Do not expose it to the public internet or place it behind a remote tunnel. It does not have accounts, multiuser authorization, or a public hosting configuration.

## Plugin edition

The package is in [`plugins/coursekin`](plugins/coursekin). It contains a plugin manifest and a tutoring skill. It uses the host's existing model, native attachments, file tools and conversation UI. The custom upload screen shown above belongs to the standalone app. The plugin follows the same three step flow in conversation.

The plugin has no Coursekin server, credentials or background uploads. File access, retention and availability across chats follow the host product. Classes do not automatically synchronize between the plugin and local app.

Coursekin 0.1.0 is approved and published in the [OpenAI plugin directory](https://chatgpt.com/plugins/plugins_6aaa22656ccc8191902ee998a70c8a86). The package passes the local manifest validator, installs in Codex, and passes the portal's automated skill scan. Full tutoring behavior in a fresh host chat remains a separate acceptance check. See [plugin test cases and publishing status](docs/plugin-release.md).

The release also includes `coursekin-plugin.zip` for hosts that support local plugin package installation. After installation, start a new chat and choose Coursekin, then provide your class name and attach your textbook and syllabus.

## Development

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m coursekin.server
```

Set `COURSEKIN_PORT` to change the local port or `COURSEKIN_DATA_DIR` to choose a different database directory. The frontend is plain HTML, CSS and JavaScript, with no build step, CDN, analytics or remote font requests.

Read [security boundaries](SECURITY.md), [design references](docs/design-sources.md), and [verification notes](docs/verification.md) for the implementation scope and tested behavior.

[Privacy](PRIVACY.md) · [Usage information](TERMS.md). Copyright 2026 Alexander Gregory Ammann. Coursekin code and original project assets are available under the MIT License. Uploaded course materials retain their own rights.
