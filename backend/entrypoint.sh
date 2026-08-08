#!/bin/sh
set -eu

python -m backend.app.init_db
exec python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
