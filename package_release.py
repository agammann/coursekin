"""Build shareable archives from an explicit file allowlist, never the working tree."""
import json
import os
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOP_FILES = {'README.md', 'SECURITY.md', 'PRIVACY.md', 'TERMS.md', 'LICENSE', 'VERSION', 'STABILITY.md', 'CHANGELOG.md', 'THIRD_PARTY_NOTICES.md', 'requirements.txt', '.gitignore', '.gitattributes', 'bootstrap.py', 'setup_key.py', 'launch.py', 'Start Coursekin.cmd', 'start.sh', 'package_release.py'}
DIRECTORIES = {'coursekin', 'local-web', 'web', 'plugins', 'tests', 'docs', 'examples', 'scripts', '.github'}
EXTENSIONS = {'.py', '.html', '.css', '.js', '.mjs', '.jsonc', '.svg', '.md', '.json', '.png', '.jpg', '.yml', '.yaml', '.txt'}

EXCLUDED_DIRECTORIES = {'__pycache__', 'data', '.git', '.venv', 'node_modules', 'dist', 'build', 'outputs', 'verification-artifacts', '.wrangler'}


def private_name(name):
    return name.startswith(('.env', '.dev.vars'))


def files():
    for directory, folders, names in os.walk(ROOT, followlinks=False):
        # Never enter private state or generated dependencies, at any depth.
        folders[:] = [name for name in folders if name not in EXCLUDED_DIRECTORIES and not private_name(name)]
        for name in names:
            if private_name(name):
                continue
            file = Path(directory) / name
            path = file.relative_to(ROOT)
            if (len(path.parts) == 1 and name in TOP_FILES) or (len(path.parts) > 1 and path.parts[0] in DIRECTORIES and (file.suffix in EXTENSIONS or name in {'LICENSE', '.gitignore'})):
                if file.is_symlink() or not file.resolve().is_relative_to(ROOT):
                    raise ValueError('A linked file cannot be packaged: ' + path.as_posix())
                if file.is_file():
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
