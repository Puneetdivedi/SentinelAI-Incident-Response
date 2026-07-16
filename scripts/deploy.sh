#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -f .env ]; then
  echo ".env not found. Copy .env.example to .env and fill in your values first."
  exit 1
fi

docker compose up --build -d

echo "Deployment started."
echo "Backend: http://localhost:8000/health"
echo "Frontend: http://localhost:5173"
