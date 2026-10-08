"""Package exact committed source and plugin snapshots, with immutable checksums."""
import hashlib, json, os, re, subprocess, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
git = lambda *args: subprocess.check_output(['git', *args], cwd=ROOT)
if Path.cwd().resolve() != ROOT:
    raise ValueError('Run packaging from the repository root.')
if git('status', '--porcelain', '--untracked-files=normal').strip():
    raise ValueError('Packaging requires a clean committed source tree.')
metadata = json.loads((ROOT / 'web/package.json').read_text())
version = (ROOT / 'VERSION').read_text().strip()
if not re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', version) or metadata.get('version') != version or metadata.get('name') != 'coursekin-browser' or metadata.get('license') != 'MIT':
    raise ValueError('Expected stable Coursekin version and MIT metadata.')
commit = git('rev-parse', 'HEAD').decode().strip()
if os.environ.get('GITHUB_SHA', commit) != commit:
    raise ValueError('Checkout differs from the workflow commit.')
tracked = git('ls-files', '-z').decode().split('\0')[:-1]
for name in tracked:
    file = ROOT / name
    if file.is_symlink() or not file.is_file():
        raise ValueError('Release contains a linked or missing source file.')
    if any(part in {'.git', 'node_modules', '.venv', '.wrangler', 'data', 'outputs', 'dist', 'release-artifacts'} or part.startswith(('.env', '.dev.vars')) for part in Path(name).parts):
        raise ValueError('Release contains private or generated state.')
    data = file.read_bytes()
    if re.search(rb'sk-(?:proj-)?[A-Za-z0-9_-]{20,}', data) or (b'-----BEGIN' + b' PRIVATE KEY-----') in data:
        raise ValueError('Release contains a secret pattern.')
out = ROOT / 'release-artifacts'; out.mkdir(exist_ok=True)
source = out / 'coursekin-local-source.zip'
subprocess.run(['git', 'archive', '--format=zip', '--prefix=coursekin/', '--output=' + str(source), 'HEAD'], cwd=ROOT, check=True)
plugin_files = [name for name in tracked if name.startswith('plugins/coursekin/')]
if len(plugin_files) != 6:
    raise ValueError('Expected the six-file Coursekin plugin bundle.')
with zipfile.ZipFile(out / 'coursekin-plugin.zip', 'w', zipfile.ZIP_DEFLATED) as package:
    package.comment = commit.encode()
    for name in sorted(plugin_files):
        package.writestr(name.removeprefix('plugins/coursekin/'), git('show', 'HEAD:' + name))
lines = []
for name in ['coursekin-local-source.zip', 'coursekin-plugin.zip']:
    with zipfile.ZipFile(out / name) as package:
        if package.testzip() is not None:
            raise ValueError('ZIP integrity failure.')
    line = hashlib.sha256((out / name).read_bytes()).hexdigest() + '  ' + name + '\n'
    (out / (name + '.sha256')).write_bytes(line.encode())
    lines.append(line)
(out / 'SHA256SUMS').write_bytes(''.join(lines).encode())
print(json.dumps({'version': version, 'commit': commit, 'sourceFiles': len(tracked), 'pluginFiles': len(plugin_files), 'archives': ['coursekin-local-source.zip', 'coursekin-plugin.zip']}))
