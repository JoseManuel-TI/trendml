#!/bin/bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
backend/.venv/bin/python -m unittest discover -s tests -v
(cd frontend && npm run build)
