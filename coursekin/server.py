import base64
import hmac
import json
import mimetypes
import os
import re
import secrets
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from .store import Store
from .provider import load_environment, answer, ProviderError, DEFAULT_MODEL

ROOT = Path(__file__).resolve().parents[1]
MAX_BODY = 84 * 1024 * 1024

class BadRequest(Exception):
    def __init__(self, message, status=400):
        self.status = status
        super().__init__(message)

def prepare_documents(items):
    if not isinstance(items, list) or not 1 <= len(items) <= 2:
        raise BadRequest('Add one or two documents at a time.')
    prepared = []
    for item in items:
        if not isinstance(item, dict) or item.get('role') not in ('textbook', 'syllabus'):
            raise BadRequest('Choose textbook or syllabus for each document.')
        name = item.get('name', '')
        if not isinstance(name, str) or not 1 <= len(name) <= 160 or '/' in name or '\\' in name:
            raise BadRequest('Invalid document name.')
        try:
            if 'text' in item:
                if not isinstance(item['text'], str) or len(item['text']) > 8_000_000:
                    raise BadRequest('Pasted text is too large.')
                raw = item['text'].encode('utf-8')
                name = name if name.endswith(('.txt', '.md')) else name + '.txt'
            else:
                raw = base64.b64decode(item.get('data', ''), validate=True)
        except (ValueError, TypeError):
            raise BadRequest('This upload could not be decoded.') from None
        if len(raw) > 30 * 1024 * 1024:
            raise BadRequest('Each document must be smaller than 30 MB.', 413)
        try:
            # Readers never need provider credentials or user supplied Python paths.
            reader_env = {k: v for k, v in os.environ.items() if k.upper() in {'SYSTEMROOT', 'WINDIR', 'PATH', 'TEMP', 'TMP', 'LANG', 'LC_ALL'}}
            result = subprocess.run([sys.executable, '-m', 'coursekin.documents', name], input=raw, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, cwd=ROOT, timeout=45, check=True, env=reader_env)
            decoded = json.loads(result.stdout)
        except subprocess.TimeoutExpired:
            raise BadRequest('Reading this file took too long. Please upload a smaller section.') from None
        except Exception:
            raise BadRequest('Could not read this file. Try a searchable PDF or paste its text.') from None
        if 'error' in decoded:
            raise BadRequest(decoded['error'])
        prepared.append({'name': name, 'role': item['role'], 'chunks': decoded['chunks']})
    return prepared

class LocalServer(ThreadingHTTPServer):
    daemon_threads = True
    request_queue_size = 8
    def __init__(self, address, store, responder=answer):
        super().__init__(address, Handler)
        self.store = store
        self.responder = responder
        self.token = secrets.token_urlsafe(32)
        self.work = threading.BoundedSemaphore(2)
        self.connections = threading.BoundedSemaphore(16)
        self.chat_lock = threading.Lock()
        self.last_calls = []
        self.port = self.server_address[1]
        self.hosts = {f'127.0.0.1:{self.port}', f'localhost:{self.port}'}

    def process_request(self, request, client_address):
        if not self.connections.acquire(blocking=False):
            self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except Exception:
            self.connections.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self.connections.release()

class Handler(BaseHTTPRequestHandler):
    server_version = 'Coursekin'
    def setup(self):
        super().setup()
        self.connection.settimeout(30)

    def log_message(self, *_):
        pass

    def send(self, status, payload, content_type='application/json; charset=utf-8', disposition=None):
        raw = payload if isinstance(payload, bytes) else json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; font-src 'self'; frame-ancestors 'none'; form-action 'none'; base-uri 'none'")
        if disposition:
            self.send_header('Content-Disposition', disposition)
        self.end_headers()
        try:
            self.wfile.write(raw)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def boundary(self):
        if self.headers.get('Host') not in self.server.hosts:
            raise BadRequest('Unrecognized host.', 403)
        origin = self.headers.get('Origin')
        if origin and origin not in {'http://' + h for h in self.server.hosts}:
            raise BadRequest('Requests from other websites are not allowed.', 403)
        if self.headers.get('Sec-Fetch-Site') == 'cross-site':
            raise BadRequest('Requests from other websites are not allowed.', 403)

    def authorize(self):
        supplied = self.headers.get('X-Coursekin-Token', '')
        if not hmac.compare_digest(supplied, self.server.token):
            raise BadRequest('Reload Coursekin to reconnect your session.', 401)

    def read_json(self, maximum=MAX_BODY):
        if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            raise BadRequest('Use application/json.', 415)
        try:
            length = int(self.headers.get('Content-Length', '0'))
        except ValueError:
            raise BadRequest('Invalid request length.')
        if not 0 < length <= maximum or self.headers.get('Transfer-Encoding'):
            self.close_connection = True
            raise BadRequest('Request is too large or has no length.', 413)
        raw = self.rfile.read(length)
        if len(raw) != length:
            raise BadRequest('Upload was interrupted.')
        try:
            value = json.loads(raw)
            if not isinstance(value, dict):
                raise ValueError()
            return value
        except (ValueError, UnicodeDecodeError):
            raise BadRequest('Invalid request data.') from None

    def do_GET(self):
        self.handle_request('GET')
    def do_POST(self):
        self.handle_request('POST')
    def do_DELETE(self):
        self.handle_request('DELETE')

    def handle_request(self, method):
        acquired = False
        try:
            self.boundary()
            path = urlsplit(self.path).path
            if method == 'GET' and path == '/api/session':
                return self.send(200, {'token': self.server.token, 'configured': bool(os.environ.get('OPENAI_API_KEY')), 'model': os.environ.get('OPENAI_MODEL', DEFAULT_MODEL)})
            if path.startswith('/api/'):
                self.authorize()
            if method == 'GET' and path == '/api/courses':
                return self.send(200, self.server.store.list())
            match = re.fullmatch(r'/api/courses/([a-f0-9]{32})(?:/(chat|documents|export))?', path)
            course = None
            if match:
                cid, action = match.groups()
                course = self.server.store.get(cid)
                if not course:
                    raise BadRequest('This class was not found.', 404)
                if method == 'GET' and not action:
                    return self.send(200, course)
                if method == 'GET' and action == 'export':
                    return self.send(200, self.server.store.export(cid), disposition='attachment; filename="coursekin-class.json"')
                if method == 'DELETE' and not action:
                    # Serialize with chat/import so deleted classes cannot receive stale writes.
                    with self.server.chat_lock:
                        self.server.store.delete(cid)
                    return self.send(200, {'deleted': True})
            if method == 'POST':
                acquired = self.server.work.acquire(blocking=False)
                if not acquired:
                    raise BadRequest('Coursekin is busy. Try again in a moment.', 429)
                if path == '/api/courses' or (match and action == 'documents'):
                    payload = self.read_json()
                    if path == '/api/courses':
                        name = payload.get('name', '')
                        if not isinstance(name, str) or not 1 <= len(name.strip()) <= 100:
                            raise BadRequest('Give your class a name of up to 100 characters.')
                        items = payload.get('documents', [])
                        if not isinstance(items, list) or {d.get('role') for d in items if isinstance(d, dict)} != {'textbook', 'syllabus'}:
                            raise BadRequest('Add both a textbook and a syllabus to start your class.')
                        if len(self.server.store.list()) >= 100:
                            raise BadRequest('You have reached 100 classes. Export and remove an old class first.')
                    elif len(course['documents']) >= 20:
                        raise BadRequest('This class has reached its 20 document limit.')
                    docs = prepare_documents(payload.get('documents'))
                    with self.server.chat_lock:
                        if path == '/api/courses':
                            if len(self.server.store.list()) >= 100:
                                raise BadRequest('You have reached the 100 class limit.')
                            result = self.server.store.create(name.strip(), docs)
                        else:
                            current = self.server.store.get(cid)
                            if not current:
                                raise BadRequest('This class was removed.', 404)
                            if len(current['documents']) + len(docs) > 20:
                                raise BadRequest('This class has a 20 document limit.')
                            result = self.server.store.add_documents(cid, docs)
                    return self.send(201, result)
                if match and action == 'chat':
                    payload = self.read_json(30_000)
                    question = payload.get('question', '')
                    if not isinstance(question, str) or not 1 <= len(question.strip()) <= 6000:
                        raise BadRequest('Ask a question of up to 6,000 characters.')
                    if not self.server.chat_lock.acquire(blocking=False):
                        raise BadRequest('Wait for the current answer to finish.', 409)
                    try:
                        now = time.monotonic()
                        self.server.last_calls = [t for t in self.server.last_calls if now - t < 60]
                        if len(self.server.last_calls) >= 10:
                            raise BadRequest('Please wait a minute before asking more questions.', 429)
                        self.server.last_calls.append(now)
                        course = self.server.store.get(cid)
                        if not course:
                            raise BadRequest('This class was removed.', 404)
                        if len(course['messages']) >= 1000:
                            raise BadRequest('This conversation is full. Export it and create a fresh class.')
                        recent = ' '.join(m['text'][:400] for m in course['messages'][-4:] if m['role'] == 'user')
                        passages = self.server.store.search(cid, question + ' ' + recent)
                        result = self.server.responder(question.strip(), passages, course['messages'])
                        # Only real retrieved IDs can become clickable references.
                        valid = {p['number'] for p in passages}
                        result = re.sub(r'\[(\d+)\]', lambda m: m.group(0) if int(m.group(1)) in valid else '[source unavailable]', result)
                        used = {int(n) for n in re.findall(r'\[(\d+)\]', result)}
                        sources = [p for p in passages if p['number'] in used]
                        self.server.store.save_exchange(cid, question.strip(), result, sources)
                        return self.send(200, {'role': 'assistant', 'text': result, 'sources': sources})
                    finally:
                        self.server.chat_lock.release()
                raise BadRequest('This endpoint does not exist.', 404)
            if method == 'GET':
                public = {'/': 'index.html', '/app.js': 'app.js', '/style.css': 'style.css', '/favicon.svg': 'favicon.svg'}
                if path in public:
                    file = ROOT / 'web' / public[path]
                    return self.send(200, file.read_bytes(), mimetypes.guess_type(file.name)[0] or 'application/octet-stream')
            raise BadRequest('Not found.', 404)
        except BadRequest as exc:
            self.send(exc.status, {'error': str(exc)})
        except ProviderError as exc:
            self.send(502, {'error': str(exc)})
        except Exception:
            self.send(500, {'error': 'Something went wrong. Your existing classes are safe. Please try again.'})
        finally:
            if acquired:
                self.server.work.release()

def main():
    load_environment()
    data = Path(os.environ.get('COURSEKIN_DATA_DIR', ROOT / 'data'))
    data.mkdir(parents=True, exist_ok=True)
    port = int(os.environ.get('COURSEKIN_PORT', '8767'))
    server = LocalServer(('127.0.0.1', port), Store(data / 'coursekin.sqlite3'))
    print(f'Coursekin is ready at http://127.0.0.1:{server.port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == '__main__':
    main()
