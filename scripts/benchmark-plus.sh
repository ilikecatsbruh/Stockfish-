#!/usr/bin/env bash
set -euo pipefail

ENGINE="${1:-./src/stockfish}"
if [[ ! -x "$ENGINE" ]]; then
  echo "Usage: $0 [path-to-stockfish-binary]" >&2
  exit 2
fi

echo "== Stockfish++ benchmark =="
echo "Engine: $ENGINE"
"$ENGINE" bench 2>&1 | tee stockfish-bench.log
echo
echo "Full benchmark output saved to stockfish-bench.log"
