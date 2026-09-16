import base64
import io
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
import zipfile
import os
import subprocess
from unittest.mock import patch
from pathlib import Path

from coursekin.documents import extract
from coursekin.server import LocalServer, prepare_documents
from coursekin.store import Store
from coursekin.provider import ProviderError

def doc(role, text):
    return {'name': role + '.txt', 'role': role, 'text': text}

class Documents(unittest.TestCase):
    def test_pdf_text_and_blank_rejection(self):
        from pypdf import PdfWriter
        from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject
        writer = PdfWriter()
        page = writer.add_blank_page(width=612, height=792)
        blank = io.BytesIO()
        writer.write(blank)
        with self.assertRaises(ValueError):
            extract('scanned.pdf', blank.getvalue())
        font = DictionaryObject({NameObject('/Type'): NameObject('/Font'), NameObject('/Subtype'): NameObject('/Type1'), NameObject('/BaseFont'): NameObject('/Helvetica')})
        page[NameObject('/Resources')] = DictionaryObject({NameObject('/Font'): DictionaryObject({NameObject('/F1'): writer._add_object(font)})})
        content = DecodedStreamObject()
        content.set_data(b'BT /F1 12 Tf 72 720 Td (Photosynthesis uses light energy.) Tj ET')
        page[NameObject('/Contents')] = writer._add_object(content)
        output = io.BytesIO()
        writer.write(output)
        self.assertEqual(extract('book.pdf', output.getvalue())[0]['location'], 'PDF page 1')
        self.assertIn('Photosynthesis', extract('book.pdf', output.getvalue())[0]['text'])

    def test_parser_has_no_provider_credentials(self):
        parsed = json.dumps({'chunks': [{'location': 'Line 1', 'text': 'example'}]}).encode()
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-private-marker', 'OTHER_SECRET': 'also-private'}), patch('coursekin.server.subprocess.run', return_value=subprocess.CompletedProcess([], 0, parsed)) as run:
            prepare_documents([doc('textbook', 'example')])
            env = run.call_args.kwargs['env']
            self.assertNotIn('OPENAI_API_KEY', env)
            self.assertNotIn('OTHER_SECRET', env)

    def test_text_locations_and_bounds(self):
        chunks = extract('reading.txt', ('photosynthesis\n' * 120).encode())
        self.assertEqual(chunks[0]['location'], 'Lines 1 to 40')
        self.assertTrue(all(len(c['text']) <= 1700 for c in chunks))
        with self.assertRaises(ValueError):
            extract('empty.txt', b' \n')
        with self.assertRaises(ValueError):
            extract('code.exe', b'anything')

    def test_docx_and_entity_rejection(self):
        def packed(xml):
            raw = io.BytesIO()
            with zipfile.ZipFile(raw, 'w') as z:
                z.writestr('word/document.xml', xml)
            return raw.getvalue()
        xml = '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Office hours are Tuesday.</w:t></w:r></w:p></w:body></w:document>'
        self.assertIn('Tuesday', extract('syllabus.docx', packed(xml))[0]['text'])
        with self.assertRaises(ValueError):
            extract('bad.docx', packed('<!DOCTYPE x [<!ENTITY x "bad">]>' + xml))

class API(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.tmp.name) / 'test.sqlite3')
        self.calls = []
        def responder(question, passages, history):
            self.calls.append((question, passages, history))
            return 'The syllabus says 40 percent [1]. An invalid reference [999].'
        self.server = LocalServer(('127.0.0.1', 0), self.store, responder)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f'http://127.0.0.1:{self.server.port}'

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.tmp.cleanup()

    def request(self, path, payload=None, method=None, headers=None, auth=True):
        h = {'Content-Type': 'application/json'}
        if auth:
            h['X-Coursekin-Token'] = self.server.token
        h.update(headers or {})
        req = urllib.request.Request(self.url + path, data=json.dumps(payload).encode() if payload is not None else None, method=method, headers=h)
        try:
            response = urllib.request.urlopen(req)
        except urllib.error.HTTPError as exc:
            response = exc
        with response:
            return response.status, response.read(), response.headers

    def create(self, name='Biology'):
        status, body, _ = self.request('/api/courses', {'name': name, 'documents': [doc('textbook', 'Photosynthesis converts light into chemical energy.'), doc('syllabus', 'Final exam is 40 percent of the grade. Office hours Tuesday.')]})
        self.assertEqual(status, 201, body)
        return json.loads(body)

    def test_security_boundary(self):
        self.assertEqual(self.request('/api/courses', auth=False)[0], 401)
        self.assertEqual(self.request('/api/session', headers={'Origin': 'https://evil.example'})[0], 403)
        self.assertEqual(self.request('/api/session', headers={'Host': 'evil.example'})[0], 403)
        self.assertEqual(self.request('/api/session', headers={'Sec-Fetch-Site': 'cross-site'})[0], 403)
        for path in ('/.env.local', '/coursekin/provider.py', '/data/coursekin.sqlite3', '/../.env.local'):
            self.assertEqual(self.request(path)[0], 404)
        _, body, headers = self.request('/api/session', auth=False)
        self.assertEqual(set(json.loads(body)), {'token', 'configured', 'model'})
        self.assertNotIn('Access-Control-Allow-Origin', headers)
        self.assertIn("frame-ancestors 'none'", headers['Content-Security-Policy'])

    def test_import_chat_sources_export_delete(self):
        course = self.create()
        path = '/api/courses/' + course['id']
        status, body, _ = self.request(path + '/chat', {'question': 'How is the final exam graded?'})
        self.assertEqual(status, 200)
        answer = json.loads(body)
        self.assertIn('[source unavailable]', answer['text'])
        self.assertTrue(answer['sources'])
        self.assertNotIn('[999]', answer['text'])
        export = json.loads(self.request(path + '/export')[1])
        self.assertEqual(len(export['messages']), 2)
        self.assertTrue(export['passages'])
        self.assertEqual(self.request(path, method='DELETE')[0], 200)
        self.assertEqual(self.request(path)[0], 404)
        with self.store.connect() as db:
            self.assertEqual(db.execute('SELECT count(*) FROM passages').fetchone()[0], 0)

    def test_failed_import_is_atomic(self):
        payload = {'name': 'Broken', 'documents': [doc('textbook', 'Good material'), doc('syllabus', '')]}
        self.assertEqual(self.request('/api/courses', payload)[0], 400)
        self.assertEqual(self.store.list(), [])

    def test_course_isolation_and_failure_no_history(self):
        first, second = self.create('Biology'), self.create('Chemistry')
        self.store.add_documents(second['id'], [{'name': 'private.txt', 'role': 'textbook', 'chunks': [{'location': 'Line 1', 'text': 'UNIQUECHEMISTRYSECRETMARKER'}]}])
        self.assertFalse(any('UNIQUECHEMISTRYSECRETMARKER' in p['text'] for p in self.store.search(first['id'], 'UNIQUECHEMISTRYSECRETMARKER')))
        def failure(*args):
            raise ProviderError('Connection unavailable.')
        self.server.responder = failure
        self.assertEqual(self.request('/api/courses/' + first['id'] + '/chat', {'question': 'Help me'})[0], 502)
        self.assertEqual(self.store.get(first['id'])['messages'], [])

if __name__ == '__main__':
    unittest.main()
