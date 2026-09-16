# Security boundaries

Coursekin's standalone app is a local, single user service. The operating system account and local processes running as that user are trusted. This is not a multiuser or public server.

The API key lives in the server environment or the untracked `.env.local` file. That file is a local plaintext secret, protected by the account's filesystem permissions, not an encrypted vault. Never publish it or include it in backups you share. The browser receives only a temporary local session token, a boolean configuration status and the model name.

The HTTP server binds to the loopback address. It verifies the Host and Origin headers, rejects cross site browser requests, requires the session token on class endpoints, and provides no CORS access. Only four explicit frontend assets are served. CSP blocks external scripts, embedding, and arbitrary connections. User and model content is inserted as text instead of HTML.

Document extraction runs in a disposable process with a 45 second deadline and a 768 MB process memory limit. The child receives a minimal environment without API credentials. Upload size, expanded DOCX size, XML declarations, PDF decompression, page count and extracted text are bounded. Files are parsed as data and links are not fetched. Extraction isolation limits resource use; it is not a complete operating system sandbox against an unknown parser vulnerability.

Model requests go to a fixed OpenAI HTTPS endpoint. The browser cannot provide an alternate provider URL. Provider error bodies and authorization headers are not returned to the client. Source content is explicitly treated as untrusted reference data in the model instructions. The model has no tools or ability to execute source instructions. These measures constrain impact; they do not prove immunity to every prompt injection or inaccurate answer.

Classes are separated by database identifiers and query filters. Successful exchanges are saved together. Failed imports do not create a partially populated class. Invalid model citation numbers do not become source links. Export includes extracted passages and history but never credentials.

Before distributing, run the tests and the allowlist based packaging script. The script rejects keys and secret files in archives. Public deployment would need a separate authentication, storage, tenancy, transport security and abuse prevention design.

## Reporting a vulnerability

Use GitHub's private vulnerability reporting feature when available on this repository. Do not post secrets or exploit details in a public issue. If private reporting is unavailable, open a public issue asking the maintainer for a private reporting channel without including sensitive details.
