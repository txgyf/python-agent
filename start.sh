#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/backend"

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt -q
else
    source .venv/bin/activate
fi

echo "Starting InfereVal server on http://0.0.0.0:8014"
python -m uvicorn server.main:app --host 0.0.0.0 --port 8014 --reload
