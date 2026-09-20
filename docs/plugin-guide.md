# OpenAI plugin guide

[Back to Coursekin](../README.md)

The plugin brings Coursekin's tutoring guidance into a compatible OpenAI host. It uses that host's model, chat interface and attachment tools. It does not include the standalone app's custom upload screen, and you do not need a separate Coursekin API key.

## Install and start

1. Open [Coursekin in the OpenAI plugin directory](https://chatgpt.com/plugins/plugins_6aaa22656ccc8191902ee998a70c8a86).
2. Sign in if required and follow the host's install flow. Plugin availability depends on the host and account.
3. Start a new chat and select or invoke Coursekin using the host's plugin controls.
4. Give your class name and attach your textbook and syllabus using the host's attachment controls. Pasted material works too. Identify which source is the textbook and which is the syllabus.
5. Let Coursekin read both materials, then ask your first question.

For example:

> Set up Biology 101. I have attached my textbook and syllabus. Read both, then help me study from them.

Try the [fictional practice class](try-coursekin.md) if you want to start with small, shareable materials.

## During a study session

Ask for an explanation, a hint, a practice question or a check of your reasoning. For a course policy, date or source fact, ask it to show the relevant location in the textbook or syllabus. Verify important details against the original.

Keep each class in its own chat or make the class and materials explicit when switching. If a later chat cannot access earlier attachments, attach them again. File retention, reading limits and access across chats are controlled by the host.

## If something is unavailable

| Problem | Next step |
| :--- | :--- |
| No install option, or plugins are unavailable in your host | Use a host and account that support the listing, or choose the [local app](local-app.md). |
| An attachment cannot be read | Try a searchable PDF, a text copy, or paste the relevant passage. The host's own file limits apply. |
| The answer depends on material you have not provided | Attach the source. Coursekin should identify the gap instead of inventing a policy or page reference. |
| A class from the local app is missing | The two editions do not synchronize. Supply the materials in the host chat separately. |

The [GitHub release](https://github.com/agammann/coursekin/releases/latest) also includes `coursekin-plugin.zip` for hosts that explicitly support local plugin package installation. Use that host's documented installation method. The directory listing is the primary installation path; the publisher's personal marketplace commands are not a public setup requirement.

## Privacy and verification

The plugin has no Coursekin server, account connection, API key or background upload. Your attachments and conversations follow the host's privacy settings and policies. See [Privacy](../PRIVACY.md#plugin).

Version 0.1.0 was approved and published. Package validation, local Codex installation and the portal's automated skill scan passed. On September 19, 2026, a fresh ChatGPT session also passed attachment reading, source based answers, missing policy handling and one question at a time practice. See the [publication record and acceptance cases](plugin-release.md) for the precise scope.
