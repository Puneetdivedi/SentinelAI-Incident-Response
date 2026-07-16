#!/usr/bin/env bash
# Backend container entrypoint: wait for Postgres, run migrations, then serve.
set -euo pipefail

echo "Waiting for the database…"
for i in $(seq 1 30); do
  if python -c "
import asyncio, os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
async def ping():
    engine = create_async_engine(os.environ['DATABASE_URL'])
    async with engine.connect() as conn:
        await conn.execute(text('SELECT 1'))
    await engine.dispose()
asyncio.run(ping())
" 2>/dev/null; then
    echo "Database is ready."
    break
  fi
  echo "  …attempt ${i}/30"
  sleep 2
done

echo "Running migrations…"
alembic upgrade head

echo "Starting API…"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers "${UVICORN_WORKERS:-2}"
