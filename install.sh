#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/fusion360_arch_fix.py" apply
python3 "$SCRIPT_DIR/fusion360_arch_fix.py" check
