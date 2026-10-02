# Coursekin privacy

Updated October 2, 2026.

Coursekin is published by Alexander Gregory Ammann. This notice covers the Coursekin source distribution and plugin.

## Public website

The [browser website](https://coursekin.alx21.chatgpt.site) reads uploaded files locally and stores extracted text, class names and conversations in IndexedDB on this device. Device mode processes questions locally. Optional **OpenAI with your key** sends your question, up to six selected excerpts with filenames/page numbers and the last four conversation messages through the Coursekin server to OpenAI. Original file binaries are not uploaded. Usage is billed to your OpenAI API account. The server uses only the key supplied with that request and does not save it in a Coursekin database or logs. The key remains in tab memory and clears when you use **Clear key**, switch to device mode, leave the page or reload; class backups exclude it. Hosted requests use `store: false`, which does not override OpenAI's retention or abuse-monitoring policies.

Public hosts supply pinned document-reader code, model runtime files and weights. Hosting and asset hosts may process ordinary request metadata. Exported class backups contain extracted materials and conversations, and are not encrypted. Delete documents or classes in the interface; browser data deletion is not secure erasure of disk sectors or exported copies. Clearing browser storage can remove all classes and cached models. Answers are drafts with source references, not guarantees of accuracy.

## Local app

The app stores extracted course text, class names and conversations in a SQLite database on your computer. Original uploaded file binaries are processed temporarily and are not retained as stored course files. Deleting a class removes its records from the app, but is not a secure erase of disk sectors or copies you exported or backed up.

Your own API key is saved in a local configuration file. The key is sent only to OpenAI to authenticate API requests. The application sends your questions, recent conversation and selected course excerpts to OpenAI to generate answers. Requests disable response storage with `store: false`; this does not override provider retention or abuse monitoring policies. See [OpenAI API data controls](https://platform.openai.com/docs/guides/your-data).

The Python local app has no publisher-hosted database, analytics, advertising trackers or telemetry endpoint. Its provider requests go from your local server to OpenAI. Files you voluntarily post to GitHub issues are public, so never include private course files, credentials or personal records there.

## Plugin

The plugin consists of instructions used by your ChatGPT or Codex host. It has no Coursekin server, external tools, account connection or API key. Your attachments and conversations are handled by the host under its own privacy settings and policies. The plugin cannot promise local storage, deletion from provider systems or availability of attachments in later conversations.

## Your controls and contact

Use the local app's class deletion and export controls for local records. Manage host conversations, attachments and retention using the host's own controls. Keep exports private. For general privacy questions, open an issue at [Coursekin support](https://github.com/agammann/coursekin/issues) without including sensitive information. For a security vulnerability, use [private vulnerability reporting](https://github.com/agammann/coursekin/security/advisories/new) when enabled, or the instructions in [SECURITY.md](SECURITY.md).
