from pathlib import Path
import sys
import zipfile
import tempfile
import unittest
from unittest.mock import patch

import package_release


class PackageIsolation(unittest.TestCase):
    def test_virtual_environment_links_are_excluded_but_source_links_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            # Match the packager's resolved root, including Windows temp-path aliases.
            root = Path(directory).resolve()
            (root / 'README.md').write_text('Coursekin')
            (root / '.venv/bin').mkdir(parents=True)
            try:
                (root / '.venv/bin/python').symlink_to(sys.executable)
            except OSError:
                self.skipTest('Creating symlinks is unavailable on this account')
            with patch.object(package_release, 'ROOT', root):
                self.assertEqual([str(relative) for _, relative in package_release.files()], ['README.md'])
                (root / 'web').mkdir()
                (root / 'web/linked.js').symlink_to(sys.executable)
                with self.assertRaisesRegex(ValueError, 'linked file'):
                    list(package_release.files())

    def test_browser_sources_ship_without_nested_private_or_generated_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            included = {'README.md', 'local-web/index.html', 'web/app.mjs', 'web/worker.mjs',
                        'web/build.mjs', 'web/package.json', 'web/package-lock.json',
                        'web/wrangler.jsonc', 'web/.openai/hosting.json'}
            excluded = {'web/.env.local', 'web/nested/.env.production.json',
                        'web/.dev.vars', 'web/nested/.dev.vars.test',
                        'web/node_modules/example/package.json', 'web/nested/node_modules/tool/index.js',
                        'web/dist/app.js', 'web/nested/build/output.js', 'web/.wrangler/state.json'}
            for name in included | excluded:
                file = root / name
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text('{}')
            with patch.object(package_release, 'ROOT', root):
                package_release.main()
            with zipfile.ZipFile(root / 'dist/coursekin-local-source.zip') as archive:
                self.assertEqual(set(archive.namelist()), {'coursekin/' + name for name in included})
