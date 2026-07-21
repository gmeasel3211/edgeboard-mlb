#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
[ -f .env ] || cp .env.example .env
[ -d .venv ] || python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo "Open .env and add ODDS_API_KEY before relying on live picks."
echo "Starting EdgeBoard at http://localhost:8000"
uvicorn app.main:app --host 127.0.0.1 --port 8000
