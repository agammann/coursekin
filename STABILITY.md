# Coursekin v1

The 1.0.0 source release contains the browser workspace, Python local app and host plugin instruction bundle. They have separate storage. The directory plugin remains version 0.1.0; installing a source ZIP does not update that listing.

## Supported behavior

- Browser classes import readable PDF, DOCX, TXT and Markdown locally, retain extracted text and conversation, expose cited excerpts, and support backup export/import, removal, deletion and reload.
- Browser answers run on experimental Qwen 3 4B with compatible WebGPU hardware, or on OpenAI with the visitor's key. Hosted mode defaults to GPT-5.4. Download and answer cancellation preserve prior work. No automatic paid fallback is provided.
- The Python app runs on loopback with Python 3.12 or newer. It imports files or pasted textbook/syllabus text, stores classes in SQLite, and uses its configured OpenAI provider, defaulting to GPT-5.4. Source-reference validation rejects unknown numeric citations before saving.
- The plugin directs a host with working file access to read both sources, verify locations, distinguish absent facts and conflicting sources, and give tutoring help. The host controls installation, attachments, model choice and retention.

Source references expose passages used. They are not guarantees of correctness, complete retrieval or reasoning. Device answers are experimental. Review calculations, dates and policies against originals.

## Recovery and upgrades

Browser backup format `coursekin-browser`, version 1, includes extracted text and conversation source snippets. Import creates a new class. Keep backups private and retain originals. Browser profiles and origins have separate data and model caches.

For the local app, stop the server before copying or restoring the complete data folder. The default is `data/`; `COURSEKIN_DATA_DIR` can choose another folder. Readable class exports are for inspection, not restoration. Copy private configuration separately and never include it in a shared release.

Use the release ZIP and checksum files as one snapshot. Dependencies are pinned in Python requirements and the browser lockfile. Run matching checks when changing code. The published release remains unchanged when later commits arrive on main; a subsequent version needs its own verification.

## Outside v1

There is no account sync, multiuser Python server, original-file backup, OCR, guaranteed interpretation of diagrams/equations, or native WebMCP interface. Interactive macOS/Linux launcher use and current directory-plugin installation depend on their environments; CI and source-bundle checks are described separately in the verification guide.
