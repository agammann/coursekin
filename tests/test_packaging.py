from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import package_release


class PackageIsolation(unittest.TestCase):
    def test_virtual_environment_links_are_excluded_but_source_links_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
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
