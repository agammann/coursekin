"""Check the local edition's entry point and the assets included in its archive."""
from html.parser import HTMLParser
from pathlib import Path
import shutil
import tempfile
import threading
import unittest
import urllib.request
import zipfile
from unittest.mock import patch

import coursekin.server as server_module
from coursekin.server import LocalServer
from coursekin.store import Store
import package_release


class Assets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = []
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'script' and attrs.get('src'):
            self.scripts.append(attrs['src'])
            self.paths.append(attrs['src'])
        if tag == 'link' and attrs.get('href'):
            self.paths.append(attrs['href'])


class LocalFrontend(unittest.TestCase):
    def assert_frontend(self, root):
        with tempfile.TemporaryDirectory() as directory, patch.object(server_module, 'ROOT', root):
            server = LocalServer(('127.0.0.1', 0), Store(Path(directory) / 'test.sqlite3'))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                base = f'http://127.0.0.1:{server.port}'
                with urllib.request.urlopen(base) as response:
                    page = response.read().decode()
                    self.assertIn('id="setup-documents"', page)
                    self.assertIn("connect-src 'self'", response.headers['Content-Security-Policy'])
                assets = Assets()
                assets.feed(page)
                self.assertEqual(assets.scripts, ['/app.js'])
                for path in assets.paths:
                    with self.subTest(asset=path), urllib.request.urlopen(base + path) as response:
                        self.assertEqual(response.status, 200)
                        self.assertTrue(response.read())
                        self.assertNotIn('application/json', response.headers['Content-Type'])
            finally:
                server.shutdown()
                server.server_close()
                thread.join()

    def test_local_entry_point_and_assets(self):
        self.assert_frontend(package_release.ROOT)

    def test_built_archive_keeps_local_entry_point_and_assets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = (Path(directory) / 'source').resolve()
            root.mkdir()
            # Stage only allowed source files; no private configuration is copied.
            for source, relative in package_release.files():
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
            with patch.object(package_release, 'ROOT', root):
                package_release.main()
            extracted = Path(directory) / 'extracted'
            with zipfile.ZipFile(root / 'dist/coursekin-local-source.zip') as archive:
                archive.extractall(extracted)
            self.assert_frontend(extracted / 'coursekin')


if __name__ == '__main__':
    unittest.main()
