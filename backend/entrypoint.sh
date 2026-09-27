#!/bin/sh
set -eu

alembic -c alembic.ini upgrade head

if [ "${RUN_SEED:-false}" = "true" ]; then
  python seed.py
fi

exec uvicorn app.main:app --host "${API_HOST:-0.0.0.0}" --port "${API_PORT:-8000}"
