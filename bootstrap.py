"""Prepare or repair the local environment before starting Coursekin."""
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
CHECK = """
import importlib.metadata as m
import sys
assert sys.version_info >= (3, 12)
assert m.version('pypdf') == '6.10.0'
if sys.platform == 'darwin':
    assert m.version('psutil') == '7.2.2'
"""


def prepare(root=ROOT):
    if sys.version_info < (3, 12):
        raise RuntimeError('Install Python 3.12 or newer from https://www.python.org/downloads/.')
    python = root / '.venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    if not python.is_file():
        print('Creating the Coursekin environment...', flush=True)
        subprocess.run([sys.executable, '-m', 'venv', str(root / '.venv')], check=True)
    if subprocess.run([str(python), '-c', CHECK], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode:
        print('Installing or repairing Coursekin dependencies...', flush=True)
        subprocess.run([str(python), '-m', 'ensurepip', '--upgrade'], check=True)
        subprocess.run([str(python), '-m', 'pip', 'install', '-r', str(root / 'requirements.txt')], check=True)
        subprocess.run([str(python), '-c', CHECK], check=True)
    return python


def main():
    try:
        python = prepare()
        if not (ROOT / '.env.local').exists() and not os.environ.get('OPENAI_API_KEY'):
            subprocess.run([str(python), str(ROOT / 'setup_key.py')], check=True)
        return subprocess.call([str(python), str(ROOT / 'launch.py')], cwd=ROOT)
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        # Never include environment values or key input in diagnostics.
        print('Coursekin could not start: ' + str(exc), file=sys.stderr)
        print('Check Python and your internet connection, then run the launcher again. See docs/local-app.md.', file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 0


if __name__ == '__main__':
    raise SystemExit(main())
