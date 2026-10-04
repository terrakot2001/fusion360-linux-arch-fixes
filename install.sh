#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ $EUID -eq 0 ]]; then
  echo "Do not run this installer as root. Run it as your normal desktop user." >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  if command -v pacman >/dev/null 2>&1; then
    echo "python3 is required; installing it with pacman..."
    sudo pacman -S --needed --noconfirm python
  else
    echo "python3 is required and could not be installed automatically." >&2
    exit 2
  fi
fi

BASE="${XDG_DATA_HOME:-$HOME/.local/share}/fusion360-linux"
CFG="${XDG_CONFIG_HOME:-$HOME/.config}/fusion360-linux/config"

if [[ -f "$BASE/launch-fusion.sh" && -f "$CFG" ]]; then
  echo "Existing Fusion Linux installation detected."
  echo "Applying/refreshing Arch compatibility fixes..."
  python3 "$ROOT/fusion360_arch_fix.py" apply
  python3 "$ROOT/fusion360_arch_fix.py" check
  echo
  echo "Repair/update complete."
  exit 0
fi

echo "No existing Fusion Linux installation detected."
echo "Starting full Arch/CachyOS installation..."
exec python3 "$ROOT/fusion360_bootstrap.py" "$@"
