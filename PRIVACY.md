# Coursekin privacy

Effective September 15, 2026.

Coursekin is published by Alexander Gregory Ammann. This notice covers the Coursekin source distribution and plugin.

## Public website

The public entry website at [coursekin.alx21.chatgpt.site](https://coursekin.alx21.chatgpt.site) is hosted by OpenAI Sites. It contains links to the plugin and local download, with no Coursekin upload form, API key field, chat service or analytics script. Hosting infrastructure may process request information under its own policies. Following an external link takes you to that service and its privacy practices.

## Local app

The app stores extracted course text, class names and conversations in a SQLite database on your computer. Original uploaded file binaries are processed temporarily and are not retained as stored course files. Deleting a class removes its records from the app, but is not a secure erase of disk sectors or copies you exported or backed up.

Your own API key is saved in a local configuration file. The key is sent only to OpenAI to authenticate API requests. The application sends your questions, recent conversation and selected course excerpts to OpenAI to generate answers. Requests disable response storage with `store: false`; this does not override provider retention or abuse monitoring policies. See [OpenAI API data controls](https://platform.openai.com/docs/guides/your-data).

Coursekin has no publisher hosted database, analytics, advertising trackers or telemetry endpoint. The publisher does not receive your course uploads, questions or API key through the app. Files you voluntarily post to GitHub issues are public, so never include private course files, credentials or personal records there.

## Plugin

The plugin consists of instructions used by your ChatGPT or Codex host. It has no Coursekin server, external tools, account connection or API key. Your attachments and conversations are handled by the host under its own privacy settings and policies. The plugin cannot promise local storage, deletion from provider systems or availability of attachments in later conversations.

## Your controls and contact

Use the local app's class deletion and export controls for local records. Manage host conversations, attachments and retention using the host's own controls. Keep exports private. For general privacy questions, open an issue at [Coursekin support](https://github.com/agammann/coursekin/issues) without including sensitive information. For a security vulnerability, use [private vulnerability reporting](https://github.com/agammann/coursekin/security/advisories/new) when enabled, or the instructions in [SECURITY.md](SECURITY.md).
