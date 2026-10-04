#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "== Python compile =="
python3 -m py_compile fusion360_arch_fix.py

echo "== Unit tests =="
python3 -m unittest discover -s tests -v

echo "== Bash syntax =="
bash -n install.sh check.sh publish-to-github.sh scripts/*.sh

if command -v shellcheck >/dev/null 2>&1; then
  echo "== ShellCheck =="
  shellcheck install.sh check.sh publish-to-github.sh scripts/*.sh
else
  echo "== ShellCheck =="
  echo "shellcheck not installed; skipping static shell analysis"
fi

echo "All available self-tests passed."
