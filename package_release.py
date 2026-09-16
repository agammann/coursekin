"""Build shareable archives from an explicit file allowlist, never the working tree."""
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOP_FILES = {'README.md', 'SECURITY.md', 'requirements.txt', '.gitignore', '.gitattributes', 'setup_key.py', 'launch.py', 'Start Coursekin.cmd', 'start.sh', 'package_release.py'}
DIRECTORIES = {'coursekin', 'web', 'plugins', 'tests', 'docs', '.github'}
EXTENSIONS = {'.py', '.html', '.css', '.js', '.svg', '.md', '.json', '.png', '.jpg', '.yml', '.yaml', '.txt'}

def files():
    for file in ROOT.rglob('*'):
        if not file.is_file():
            continue
        path = file.relative_to(ROOT)
        if file.is_symlink() or not file.resolve().is_relative_to(ROOT):
            raise ValueError('A linked file cannot be packaged: ' + path.as_posix())
        if '__pycache__' in path.parts:
            continue
        if (len(path.parts) == 1 and file.name in TOP_FILES) or (len(path.parts) > 1 and path.parts[0] in DIRECTORIES and file.suffix in EXTENSIONS):
            if any(part.startswith('.env') or part in {'data', '.git', '.venv', 'node_modules'} for part in path.parts):
                raise ValueError('Private path found: ' + path.as_posix())
            yield file, path

def check(data, label, key=None):
    if re.search(rb'sk-(?:proj-)?[A-Za-z0-9_-]{20,}', data) or (b'-----BEGIN' + b' PRIVATE KEY-----') in data or (key and key in data):
        raise ValueError('Secret found in ' + label)

def main():
    key = None
    env = ROOT / '.env.local'
    if env.exists():
        for line in env.read_text(encoding='utf-8-sig').splitlines():
            if line.startswith('OPENAI_API_KEY='):
                key = line.split('=', 1)[1].strip().strip('\"\'').encode()
    out = ROOT / 'dist'
    out.mkdir(exist_ok=True)
    selected = sorted(files(), key=lambda item: str(item[1]))
    with zipfile.ZipFile(out / 'coursekin-local-source.zip', 'w', zipfile.ZIP_DEFLATED) as source, zipfile.ZipFile(out / 'coursekin-plugin.zip', 'w', zipfile.ZIP_DEFLATED) as plugin:
        for file, relative in selected:
            data = file.read_bytes()
            check(data, relative.as_posix(), key)
            source.writestr('coursekin/' + relative.as_posix(), data)
            if relative.parts[:2] == ('plugins', 'coursekin'):
                plugin.writestr('/'.join(relative.parts[2:]), data)
    for archive in out.glob('*.zip'):
        with zipfile.ZipFile(archive) as z:
            if z.testzip() is not None:
                raise ValueError('Archive integrity check failed.')
            for member in z.infolist():
                check(z.read(member), member.filename, key)
    print(json.dumps({'source_files': len(selected), 'archives': ['coursekin-local-source.zip', 'coursekin-plugin.zip'], 'secret_scan': 'passed', 'private_data': 'excluded'}))

if __name__ == '__main__':
    main()
