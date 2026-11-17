# Changelog

## 1.0.1

- Clear stale reading status after a failed browser question or material import while preserving the error, question, saved class and cancellation behavior.
- Select pypdf 7.0.1, the upstream patched release for [GHSA-fhff-j4m8-439h](https://github.com/py-pdf/pypdf/security/advisories/GHSA-fhff-j4m8-439h), in both dependency installation and launcher checks. Coursekin's bounded PDF text extraction remains unchanged.
- Align source version metadata and dependency notices with the shipped requirements and browser lockfile. The instruction-only plugin remains version 0.1.0.

## 1.0.0

Coursekin's first combined source release contains the browser workspace, Python local app and host tutoring bundle with separate setup and recovery guides.

- Browser saves update visible and exported state only after IndexedDB succeeds, so an aborted save cannot leak an unsaved answer into a backup.
- PDF and DOCX readers use current patched releases. PDF workers close after successful extraction and unreadable files, allowing the next import to proceed.
- The Python provider defaults to GPT-5.4 and validates structured numeric source references before saving.
- Available compatible dependency patches, fictional practice files, browser recovery checks, exact source packaging and release checksums are included.
- The directory-plugin bundle remains version 0.1.0 and retains its host-specific installation and attachment boundaries.
