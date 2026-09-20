# Verification

Initial checks ran on Windows with Python 3.12 and the Codex in app browser on September 15, 2026. The follow-up below records live checks on September 19. Historical checks are preserved rather than presented as newly rerun evidence.

## September 19 real usage checks

Downloaded the public v0.1.0 source ZIP into a fresh directory and created a new Python virtual environment. In the actual browser UI, imported the fictional PDF textbook and DOCX syllabus, asked a live OpenAI question spanning both sources, opened the matching syllabus citation and reloaded the saved conversation. The answer correctly identified 40 percent and thylakoid membranes. No local app console warnings or errors were observed. Desktop and a narrow mobile viewport rendered without horizontal overflow.

A separate live HTTP flow imported an original 100 page fictional PDF and syllabus. Retrieval found the invented Lumenfern pigment fact on PDF page 87 and combined it with the correct 65 percent exam weight from that class's syllabus. A missing policy question correctly identified absent information. Export contained the four saved messages and extracted passages, with no API key fields. A malformed PDF was rejected without creating a partial class. Deleting that disposable test class removed it.

The published plugin was installed from its public listing and used in a fresh ChatGPT Work conversation with the two fictional attachments. It read both, answered correctly with source locations, identified the absent late work policy, and paused after one practice question. This closes the previously pending basic fresh host tutoring check; it does not prove every proposed adversarial case or every host configuration.

Found and fixed a launcher recovery defect: a partial `.venv` caused later launches to skip dependency installation. The shared bootstrap now checks the environment and repairs missing pinned dependencies, including a missing pip installation. A newly extracted candidate archive with an intentionally incomplete environment repaired itself and the actual Windows launcher served the app successfully. Failed key enrollment now stops launch. Two regression tests cover retry behavior and rejected enrollment, and CI also exercises clean bootstrap preparation on each operating system.

These are author-run acceptance checks using fictional materials and real provider calls, not feedback from recruited students. Interactive macOS/Linux launches, very large textbooks near the resource limits, scanned PDF OCR, and broad accessibility coverage remain outside this pass.

## Completed

Eight common automated tests pass. They cover text locations and chunk bounds, PDF text and blank PDF handling, DOCX parsing and entity rejection, removal of credentials from the parser environment, HTTP Host/Origin/session boundaries, private path rejection, import atomicity, class isolation, provider failure without false history, citation number validation, export and deletion. A ninth test runs on macOS and verifies that the parent memory monitor kills an oversized reader and enforces the time limit.

[GitHub Actions run 35057979130](https://github.com/agammann/coursekin/actions/runs/35057979130) passed on Windows, Ubuntu and macOS for commit `b438178f0133c2116bf0435c13209b13619f71dd`, including tests, package creation and archive upload. The first run exposed a macOS RLIMIT_AS incompatibility; the corrected implementation uses a parent memory monitor on macOS. See SECURITY.md for its sampling limitations.

A fresh extraction of the source release archive also passes all eight tests without a key or class database. The frontend passes `node --check web/app.js`. The OpenAI plugin validator passes for `plugins/coursekin`, and the skill frontmatter validator passes. The portable manifest and legacy compatibility overlay identify the same package.

A real browser session imported a fictional PDF textbook and DOCX syllabus into Biology 101. A real OpenAI Responses API request answered a question using both sources: the final exam is 40 percent, and light dependent reactions happen in thylakoid membranes. The answer included working source references to the PDF page and syllabus paragraphs. Opening a source showed the actual extracted passage. Reloading restored the class and saved exchange. Pasted supplemental text was also imported through the materials panel after the final server restart. No browser errors or warnings were captured during this flow.

No API key values were displayed or placed in user facing outputs. The configured key stays in the server environment or private, Git ignored `.env.local`. The parser process does not inherit it. The release script checks both archive content and source candidates for key patterns and the configured key value without printing the value.

## Visual comparison

The generated design concept and actual browser screenshots were inspected with the local image viewer. The native comparison used 1505 by 1045 pixels. The mobile check used 390 by 844 pixels and confirmed that document width equals viewport width. The ordinary desktop browser viewport was also inspected.

| Comparison point | Evidence and result |
| :--- | :--- |
| Main layout | Same class rail, open canvas, centered form width and two upload areas |
| Typography | Bold sans headline with an italic serif accent; oversized first revision reduced to align with the concept |
| Copy | Headline, supporting line, field names, file guidance, paste actions, privacy note and primary CTA match the concept |
| Palette | Warm paper, dark text, pale lime textbook panel, pale lavender syllabus panel and cobalt primary button |
| Controls and icons | Outlined book and document icons, clear labels, consistent rounded controls and keyboard focus |
| Spacing | Form and upload area positions were adjusted to match the concept and fit its native viewport |
| Mobile | Compact navigation, two usable upload areas, readable privacy copy and no horizontal overflow |
| Interaction | Real file chooser/import, editable class name, real model question, citation modal and restored history |

The implementation was checked for faithful layout, hierarchy and interaction against the concept. Intentional implementation differences are native font rasterization, flat solid fills instead of incidental generated image texture, and responsive type scaling. The UI is real HTML and CSS, not an image of a form. There are no material unresolved layout mismatches in the reviewed setup screen.

## Boundaries

The generated imagery is a design reference, not proof of runtime behavior. The screenshots named `coursekin-desktop.png`, `coursekin-mobile.png` and `coursekin-chat.png` show the actual app.

The plugin was initially installed through the publisher's local personal marketplace and appeared as `coursekin:course-assistant`. This is historical publisher setup, not an installation command for other users. OpenAI's portal accepted the package, passed its skill scan and published it after the publisher's attestations. The [public directory listing](https://chatgpt.com/plugins/plugins_6aaa22656ccc8191902ee998a70c8a86) and September 19 fresh chat checks are recorded above; untested host acceptance cases remain listed in [plugin release](plugin-release.md).

The source is public at [agammann/coursekin](https://github.com/agammann/coursekin) under MIT. GitHub Actions validates all three operating systems. Interactive browser and launcher behavior was exercised on Windows; macOS and Linux interactive launches remain unverified.

The local app uses keyword retrieval. It does not implement OCR, offline inference, semantic vector retrieval, cloud accounts, class syncing or class export import. The security checks cover the stated local trust boundary and are not a claim of comprehensive vulnerability assessment.
