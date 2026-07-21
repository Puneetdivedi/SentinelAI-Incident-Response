#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

cd backend
python -m pip install -q .[dev]
ruff check .
python -m mypy app
pytest -q

cd ../frontend
npm ci
npm run lint
npm run build
