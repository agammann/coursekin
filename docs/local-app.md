# Local app guide

[Back to Coursekin](../README.md)

## Before you start

You need Python 3.12 or newer, a browser, an internet connection and your own OpenAI API key with access to the configured model. API usage uses your own billing. The [plugin edition](plugin-guide.md) uses its host model and does not need a separate key.

Download `coursekin-local-source.zip` from **Assets** on the [latest release](https://github.com/agammann/coursekin/releases/latest). Extract the entire archive, then open the `coursekin` folder containing `launch.py` and the launchers. Do not run the launcher from inside a ZIP preview or move it out of that folder.

## Windows

Install Python from [python.org](https://www.python.org/downloads/), including the Python launcher. Open a new terminal and check:

```powershell
py -3 --version
```

The version should be 3.12 or newer. Double click **Start Coursekin.cmd** in the extracted folder. It creates `.venv`, installs dependencies on first use and starts the app. If the `py` launcher is unavailable, Coursekin also tries `python` from your PATH.

For manual setup, open PowerShell in the `coursekin` folder and run:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe setup_key.py
.\.venv\Scripts\python.exe launch.py
```

These commands use the virtual environment directly; you do not need to change PowerShell's script execution policy. If several Python versions are installed, use `py -3.12 -m venv .venv` to select 3.12 explicitly.

## macOS and Linux

Check that the Python selected by your terminal is 3.12 or newer:

```sh
python3 --version
```

Open a terminal in the extracted `coursekin` folder, then run:

```sh
sh start.sh
```

For manual setup:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python setup_key.py
.venv/bin/python launch.py
```

If Linux reports that `venv` or `ensurepip` is unavailable, install the virtual environment support package for your Python version using your distribution's package manager, then retry. Automated tests run on macOS and Linux; their interactive launchers have not yet been verified manually.

## Connect your key

Create or manage your key in [OpenAI API keys](https://platform.openai.com/api-keys). Paste it only into the hidden terminal prompt from `setup_key.py`. Nothing appears as you type or paste; press Enter when finished.

The script saves the key in `.env.local` in the app folder. That file is excluded from Git and packaged releases. It is a plaintext local secret, so keep it private. Do not paste it into a GitHub issue or the public Coursekin website.

The automatic launchers skip enrollment when `.env.local` already exists or `OPENAI_API_KEY` is set in the terminal environment. **Settings** shows whether a key is configured; a successful answer is the check that it can actually call the model.

To replace a key, stop the app with Ctrl+C, run the setup command for your operating system above, and restart. The setup script replaces `.env.local`, so reapply any custom `OPENAI_MODEL` entry afterward. An existing terminal environment variable takes precedence over the file.

## Create your first class

1. Keep the launcher terminal open. The browser should open at the local address `http://127.0.0.1:8767`. If it does not, enter that address yourself.
2. Enter a class name, such as **Biology 101**.
3. Drop or browse for one textbook and one syllabus. You can use **Paste text instead** for either source.
4. Select **Start asking questions** and wait for the import to finish.
5. Ask a specific question. For a first try without your own files, use the [practice class](try-coursekin.md).

Click a numbered citation or source button beneath an answer to read the retrieved excerpt. PDF references use the file's page order, which can differ from printed page numbers.

## Return to a class and manage materials

Select a class under **Your classes**, or choose **New class** to start another. Classes and saved conversations persist across app restarts when you use the same data directory.

Open **Course materials** to add more material, export a class or delete it. Choose **Add more material** and supply one or two documents at a time, assigning each to textbook or syllabus. A class supports up to 20 documents.

**Export class** downloads a readable JSON copy of the extracted text and conversation. Treat it as private. Coursekin does not currently import these exports. **Delete class** removes the stored class records after confirmation; it leaves the original files on your computer unchanged.

Closing the browser tab does not stop the server. Press Ctrl+C in the launcher terminal to stop it. Use the same launcher to return later.

## Formats and limits

| Input | What Coursekin reads |
| :--- | :--- |
| Searchable PDF | Text with references to the PDF file's page order |
| DOCX | Main document paragraphs with paragraph locations |
| TXT or Markdown | UTF 8 text with line locations |
| Pasted text | A text document stored with its textbook or syllabus role |

Each file must be under 30 MB. PDFs are limited to 2,000 pages and each document to 8 million extracted characters. Reading a document has a 45 second deadline and platform specific memory limits. Complex files may reach those limits sooner. See [Security](../SECURITY.md) for the exact parser boundaries.

Scanned PDFs need OCR before import. Password protected files, images, tables, equations and DOCX headers or comments may not be readable or preserved. Try a searchable text copy or a smaller section when extraction fails.

Retrieval uses local keyword search. It sends selected passages, your question and recent conversation to OpenAI, rather than the entire textbook for every answer. Ask about a specific topic or paste a relevant passage if an answer misses context. A citation identifies a retrieved excerpt; it does not guarantee that every statement is correct.

## Keep your work when updating

Stop the app before copying its data. Keep a private backup of the entire `data` folder and your original source files. The default database is `data/coursekin.sqlite3`; original upload binaries are not stored in it. If you configured another data directory, back up that directory instead.

Extract the next release into a separate folder. With both copies stopped, copy the backed up `data` folder into the new app folder, then set up your key and launch it there. Check that your classes appear before removing the old copy. Read the new release notes for any data migration instructions. Do not overwrite or share your only copy of a database.

## Troubleshooting

| Problem | What to do |
| :--- | :--- |
| `py` or `python3` is not found | Install Python and open a new terminal. Check the selected version using the operating system instructions above. |
| `No module named pypdf` or an interrupted first install | Run the launcher again. Version 0.1.1 checks and repairs missing dependencies. With version 0.1.0, use the manual dependency install command or download the new release. |
| The browser says it cannot connect | Confirm the launcher is running and use the exact address printed in its terminal. Read any startup error there. |
| The port is already in use | Stop your previous Coursekin instance, or select another port using the [configuration examples](development.md#configuration). |
| “Reload Coursekin to reconnect your session” | Reload the page after restarting the local server. |
| “Connect your OpenAI API key” or “The API key was rejected” | Stop the app, rerun private key setup and restart. Check whether a terminal environment variable is overriding the saved key. |
| A model permission error | Confirm the key can use the configured model and Responses API. See [configuration](development.md#configuration). |
| A usage or rate limit error | Review your OpenAI API billing and limits, then retry later. |
| A file cannot be read or takes too long | Use a searchable PDF, a smaller section or pasted text. Check the format and size limits above. |
| A saved class seems missing | Launch the same app folder and check `COURSEKIN_DATA_DIR`. A fresh extraction has its own empty database unless you transfer your data. |

If you still need help, [open an issue](https://github.com/agammann/coursekin/issues). Include your operating system, Python version, steps and redacted error text. Never include `.env.local`, a database, private course materials or an API key.
