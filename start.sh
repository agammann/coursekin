#!/bin/sh
set -eu
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
  .venv/bin/python -m pip install -r requirements.txt
fi
if [ ! -f .env.local ] && [ -z "${OPENAI_API_KEY:-}" ]; then
  .venv/bin/python setup_key.py
fi
exec .venv/bin/python launch.py
