"""Verify both release ZIPs and extract an exact fresh source consumer."""
import argparse, hashlib, json, stat, subprocess, zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--out', required=True)
parser.add_argument('--directory')
parser.add_argument('--commit')
args = parser.parse_args()
directory = Path(args.directory).resolve() if args.directory else ROOT / 'release-artifacts'
commit = args.commit or subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')[:-1]
names = ['coursekin-local-source.zip', 'coursekin-plugin.zip']
lines = []
for name in names:
    line = hashlib.sha256((directory / name).read_bytes()).hexdigest() + '  ' + name + '\n'
    if (directory / (name + '.sha256')).read_bytes() != line.encode():
        raise ValueError('Archive checksum differs.')
    lines.append(line)
if (directory / 'SHA256SUMS').read_bytes() != ''.join(lines).encode():
    raise ValueError('Combined checksums differ.')
destination = Path(args.out).resolve()
if destination.exists() or destination.is_relative_to(ROOT):
    raise ValueError('Use a new consumer folder outside the checkout.')
def read_zip(name, prefix):
    files = {}
    with zipfile.ZipFile(directory / name) as package:
        if package.comment.decode() != commit or package.testzip() is not None:
            raise ValueError('ZIP commit or integrity differs.')
        if len(package.namelist()) != len(set(package.namelist())):
            raise ValueError('Duplicate ZIP path.')
        for entry in package.infolist():
            if not entry.filename.startswith(prefix):
                raise ValueError('ZIP prefix differs.')
            name = entry.filename[len(prefix):]
            path = PurePosixPath(name)
            if path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name:
                raise ValueError('Unsafe ZIP path.')
            if stat.S_IFMT(entry.external_attr >> 16) not in {0, stat.S_IFREG, stat.S_IFDIR}:
                raise ValueError('Linked or special ZIP member.')
            if not entry.is_dir():
                files[name] = package.read(entry)
    return files
source = read_zip(names[0], 'coursekin/')
plugin = read_zip(names[1], '')
if set(source) != set(tracked):
    raise ValueError('ZIP differs from the tracked source set.')
for name, data in source.items():
    if data != (ROOT / name).read_bytes():
        raise ValueError('ZIP source bytes differ: ' + name)
expected_plugin = {name.removeprefix('plugins/coursekin/'): data for name, data in source.items() if name.startswith('plugins/coursekin/')}
if len(expected_plugin) != 6 or plugin != expected_plugin:
    raise ValueError('Plugin ZIP differs from the exact source bundle.')
for name in ['LICENSE', 'README.md', 'VERSION', 'STABILITY.md', 'web/package-lock.json', 'examples/practice-syllabus.md']:
    if name not in source:
        raise ValueError('Missing release license, guide or sample.')
destination.mkdir(parents=True)
for name, data in source.items():
    target = destination / name; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(data)
print(json.dumps({'commit': commit, 'sourceFiles': len(source), 'pluginFiles': len(plugin), 'sourceBytes': 'match', 'consumer': str(destination)}))
