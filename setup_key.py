"""Private terminal enrollment for people running their own Coursekin copy."""
import getpass
import os
from pathlib import Path

def main():
    print('Coursekin keeps your OpenAI key in .env.local on this computer.')
    print('Create your own key at https://platform.openai.com/api-keys')
    key = getpass.getpass('Paste your API key (hidden): ').strip()
    if not key.startswith('sk-') or any(c.isspace() for c in key) or len(key) < 25:
        raise SystemExit('The key format was not recognized. Nothing was saved.')
    target = Path(__file__).resolve().parent / '.env.local'
    content = 'OPENAI_API_KEY=' + key + '\n'
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as out:
        out.write(content)
    if os.name != 'nt':
        target.chmod(0o600)
    print('Saved locally. Restart Coursekin to use the key. Never share .env.local.')

if __name__ == '__main__':
    main()
