#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null 2>&1; then
  echo "Install Python 3.10+ first: https://www.python.org/downloads/"
  exit 1
fi
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
echo "Starting Azan at http://127.0.0.1:8000 (press Ctrl+C to stop)"
exec .venv/bin/python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
