# Development and contributions

[Back to Coursekin](../README.md)

## Source setup

Clone the repository, then follow the manual Python environment and dependency setup in the [local app guide](local-app.md). Run commands from the repository root.

```sh
git clone https://github.com/agammann/coursekin.git
cd coursekin
```

No Node build, database server or frontend package installation is required. The application uses Python, SQLite and plain HTML, CSS and JavaScript.

## Run checks

On Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe package_release.py
```

On macOS or Linux:

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python package_release.py
```

Tests use temporary databases and controlled responders; they do not require a real API key or make paid model requests. CI runs tests and packaging on all three platforms. See the [verification record](verification.md) for the limits of those checks.

If you change browser JavaScript and have Node.js installed, run `node --check web/app.js`, then exercise the changed flow in the local app. A syntax check alone does not verify the interface.

## Configuration

| Variable | Default | Where to set it |
| :--- | :--- | :--- |
| `OPENAI_API_KEY` | None | Private `setup_key.py` prompt or terminal environment |
| `OPENAI_MODEL` | `gpt-4.1-mini` | Terminal environment or `.env.local` |
| `COURSEKIN_PORT` | `8767` | Terminal environment |
| `COURSEKIN_DATA_DIR` | `data` under the app folder | Terminal environment; prefer an absolute path |

Only `OPENAI_API_KEY` and `OPENAI_MODEL` are loaded from `.env.local`. Existing environment values take precedence. Restart after changing configuration. The selected model must be available to your key and support the Responses API used by the provider.

To use another local port on Windows PowerShell:

```powershell
$env:COURSEKIN_PORT = '8768'
.\.venv\Scripts\python.exe launch.py
```

On macOS or Linux:

```sh
COURSEKIN_PORT=8768 .venv/bin/python launch.py
```

To start without opening a browser, substitute `-m coursekin.server` for `launch.py`. Read the terminal for the local address. Keep the loopback binding; the app has no public hosting or multiuser authentication design.

## Repository layout

| Path | Purpose |
| :--- | :--- |
| `coursekin/` | HTTP service, document reader, resource limits, storage and model requests |
| `web/` | Local app interface and assets |
| `plugins/coursekin/` | Manifests, icon and tutoring skill |
| `tests/` | Automated behavior and security boundary checks |
| `docs/` | Guides, research, screenshots and verification records |
| `.github/workflows/checks.yml` | Windows, Ubuntu and macOS CI |
| `data/`, `.env.local`, `.venv/`, `dist/` | Private or generated files excluded from Git |

The public [Coursekin website](https://coursekin.alx21.chatgpt.site) is a separate OpenAI Sites deployment linking to the two editions. Running this repository starts the local study app.

## Package a release

Run `package_release.py` with the virtual environment's Python. It builds `dist/coursekin-local-source.zip` and `dist/coursekin-plugin.zip` from explicitly allowed paths, scans for secret patterns and the locally configured key, and verifies ZIP integrity. It does not upload anything.

The source archive contains a top level `coursekin` folder. The plugin archive contains its files at the root. Private configuration, databases, virtual environments and generated output are excluded. Inspect the result before sharing it; do not ZIP the whole working folder.

Versioned release assets are snapshots. Documentation on `main` can be newer than the bundled documents. A later software release should have its own version, release notes and verification record.

## Propose a change

For a bug, include your operating system, Python version, reproduction steps, expected result and actual result. Use fictional fixtures. For a pull request, explain the user visible change and the checks you ran; update the matching guide if behavior changes.

Do not commit keys, `.env.local`, databases, exports or private materials. Use the [security reporting process](../SECURITY.md#reporting-a-vulnerability) for sensitive findings. Contributions are distributed under the project's [MIT license](../LICENSE).
