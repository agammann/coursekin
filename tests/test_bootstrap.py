import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import bootstrap


class StartupRecovery(unittest.TestCase):
    def test_retry_repairs_existing_environment_and_stops_on_failed_install(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            python = root / '.venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
            python.parent.mkdir(parents=True)
            python.touch()
            ok = subprocess.CompletedProcess([], 0)
            missing = subprocess.CompletedProcess([], 1)
            failed = subprocess.CalledProcessError(1, ['pip', 'install'])
            # A partial environment survives a failed installation. Retrying
            # must perform installation again instead of launching the app.
            with patch('bootstrap.subprocess.run', side_effect=[missing, ok, failed]) as run:
                with self.assertRaises(subprocess.CalledProcessError):
                    bootstrap.prepare(root)
                self.assertIn('pip', run.call_args.args[0])
            with patch('bootstrap.subprocess.run', side_effect=[missing, ok, ok, ok]) as run:
                self.assertEqual(bootstrap.prepare(root), python)
                self.assertEqual(run.call_args_list[2].args[0][-2:], ['-r', str(root / 'requirements.txt')])
            with patch('bootstrap.subprocess.run', return_value=ok) as run:
                bootstrap.prepare(root)
                self.assertEqual(run.call_count, 1, 'A healthy environment must start without network installation')

    def test_rejected_key_setup_does_not_start_app(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(bootstrap, 'ROOT', Path(directory)), patch('bootstrap.prepare', return_value=Path('python')), patch.dict(os.environ, {}, clear=True), patch('bootstrap.subprocess.run', side_effect=subprocess.CalledProcessError(1, ['setup_key.py'])), patch('bootstrap.subprocess.call') as launch:
            self.assertEqual(bootstrap.main(), 1)
            launch.assert_not_called()
