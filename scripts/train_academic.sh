#!/bin/bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
PYTHON="$ROOT_DIR/backend/.venv/bin/python"
"$PYTHON" scripts/download_uci.py
"$PYTHON" scripts/prepare_uci.py --selection-cutoff 2011-08-01 --output work/uci/prepared-v2.json
"$PYTHON" scripts/train_uci_v3.py --input work/uci/prepared-v2.json
