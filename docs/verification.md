# Verification

Initial checks ran on Windows with Python 3.12 and the Codex in app browser on September 15, 2026. The follow-up below records live checks on September 19. Historical checks are preserved rather than presented as newly rerun evidence.

## October 2 local app startup repair

The current source had served the browser edition's HTML through the Python server, which did not serve its `app.mjs` entry point. A live local HTTP check reproduced `/` returning 200 while `/app.mjs` returned 404. The released local interface is now kept in `local-web/`, separate from the browser edition in `web/`.

Two new HTTP regressions check the local entry point and all linked assets, both from the source tree and from a built source ZIP. Both failed before the fix and passed afterward. The Windows Python 3.12.14 suite ran 15 tests: 13 passed; the macOS-only memory-monitor test and the symlink test were skipped on this machine. The restored local JavaScript also passed its syntax check. An archive regression verifies that browser modules and manifests are included while nested dependencies, build output, worker state and private environment files are excluded.

A fresh candidate source ZIP was extracted and started with a private test data directory and no provider credentials. In the rendered local app, a fictional two-page PDF textbook and DOCX syllabus imported into a new class, a TXT supplement was added, and export preserved the textbook's page-2 passage, syllabus facts and supplement text. Reload restored the class, and deleting it returned to the empty setup screen. Desktop (1440 × 1000) and narrow (390 × 844) views were inspected, with no horizontal overflow at the narrow size and no browser warnings, errors or failed requests.

This initial repair pass used installed Chrome and tested the Python entry point, imports, storage and packaging. A subsequent run made three real requests using the local app's unchanged default, `gpt-4.1-mini`: combined syllabus/textbook facts (40 percent and thylakoid membranes), a weighted grade (78 percent, with correct arithmetic), and an absent late-work policy (explicitly unknown). All returned HTTP 200. Four opened source dialogs matched the exported source text and locations; reload restored all three exchanges, and export contained no key. No browser warnings or errors were observed. This did not exercise a clean-machine dependency installation or repeat interactive macOS/Linux launcher testing.

## October 2 browser and hosted answers

The browser edition now offers an explicit choice between on-device inference and OpenAI using the visitor's own API key. Real model checks used fictional course materials and predeclared expected answers. They are development examples, not a general accuracy benchmark.

- **Browser model quality:** Qwen 3 1.7B answered two simple fact/absence questions correctly, but returned 240 percent for a weighted-grade question whose answer was 78 percent. It was removed from the choices. Qwen 3 4B answered all three correctly and remains labeled experimental. A further current-code run returned 78 percent, then correctly returned 73 percent after cancellation and immediate retry. Cancellation preserved the conversation and draft and released the worker; retry reloaded the cached model. These results do not establish reliability on other questions or devices.
- **Hosted quality:** Six real GPT-5.4 answers correctly handled the final-exam weight, weighted grade, missing late-work policy, pH, Chinese photosynthesis material and ATP/NADPH support for the Calvin cycle. The passages and explanations were reviewed, not only their source identifiers. Every saved quotation matched an extracted source page. GPT-5.4 mini is available but was not evaluated in this pass.
- **Actual workflows:** PDF and DOCX extraction, new drafts during generation, re-enabled Remove controls, cancellation and immediate retry, invalid-key HTTP 401 without a false conversation entry, backup restoration and key clearing all passed. The credential was absent from WebStorage, IndexedDB and exported backups. The hosted run made eight submissions: six completed answers, one canceled request and one deliberately invalid key. No page errors occurred; the invalid-key request produced the expected console HTTP error.
- **Retrieval:** A follow-up found that substring matching let `pH` match `photosynthesis`. Whole Unicode words and inverse-frequency weighting now rank the chemistry note first even after eight distracting photosynthesis files. This regression was checked with actual browser uploads without a provider request. Original quotations, Chinese, Greek and full-width text were preserved.
- **Layout and delivery:** Desktop width 1440 and mobile widths 390 and 320 had no horizontal overflow. The built Worker served the intended browser modules and returned 404 for tested server source, build/configuration, environment and dependency paths.

Automated browser tests cover backup validation and retrieval, bounded provider requests, same-origin access, unknown source identifiers, credential exclusion, safe provider errors, rejected redirects and cancellation of a stalled request upload. Their provider responses are synthetic; they verify handling, not model quality. Source markers use `[source:1]` so ordinary mathematical brackets such as `[0, 1]` are not mistaken for citations.

Scanned PDF OCR, very large materials near every resource limit, all hardware/browser combinations, broad accessibility coverage and adversarial tutoring quality remain outside this pass. Citation checks cannot prove that a claim is supported or that a calculation is correct. Earlier plugin checks below remain historical.

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

The plugin was initially installed through the publisher's local personal marketplace and appeared as `coursekin:course-assistant`. This is historical publisher setup, not an installation command for other users. The publisher completed the attestations and submitted the package; the portal accepted it after its skill scan. The [public directory listing](https://chatgpt.com/plugins/plugins_6aaa22656ccc8191902ee998a70c8a86) and September 19 fresh chat checks are recorded above; untested host acceptance cases remain listed in [plugin release](plugin-release.md).

The source is public at [agammann/coursekin](https://github.com/agammann/coursekin) under MIT. GitHub Actions validates all three operating systems. Interactive browser and launcher behavior was exercised on Windows; macOS and Linux interactive launches remain unverified.

The local app uses keyword retrieval. It does not implement OCR, offline inference, semantic vector retrieval, cloud accounts, class syncing or class export import. The security checks cover the stated local trust boundary and are not a claim of comprehensive vulnerability assessment.
