#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$ROOT/fusion360_arch_fix.py" apply
exec python3 "$ROOT/fusion360_arch_fix.py" check
