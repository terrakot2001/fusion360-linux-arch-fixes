#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT="${1:-fusion360-diagnostics-$STAMP.txt}"

sanitize_home() {
  sed "s|$HOME|~|g"
}

{
  echo "Fusion 360 Linux Arch Fixes - diagnostics"
  echo "Generated: $(date --iso-8601=seconds 2>/dev/null || date)"
  echo

  echo "== System =="
  printf 'Kernel: '
  uname -srmo 2>/dev/null || true
  if [[ -r /etc/os-release ]]; then
    grep -E '^(NAME|PRETTY_NAME|VERSION|VERSION_ID)=' /etc/os-release || true
  fi
  printf 'Desktop: %s\n' "${XDG_CURRENT_DESKTOP:-unknown}"
  printf 'Session type: %s\n' "${XDG_SESSION_TYPE:-unknown}"
  echo

  echo "== GPU =="
  if command -v lspci >/dev/null 2>&1; then
    lspci | grep -Ei 'vga|3d|display' || true
  fi
  if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>/dev/null || true
  fi
  echo

  echo "== Patcher =="
  python3 "$ROOT/fusion360_arch_fix.py" --version 2>&1 || true
  python3 "$ROOT/fusion360_arch_fix.py" check 2>&1 || true
  echo

  echo "== Autodesk callback handlers =="
  if command -v gio >/dev/null 2>&1; then
    gio mime x-scheme-handler/adskidmgr 2>&1 || true
    gio mime x-scheme-handler/adsk 2>&1 || true
  else
    echo "gio: not found"
  fi
  echo

  echo "== Relevant helper process counts =="
  printf 'toolwindow fixer: '
  pgrep -fc 'fusion-toolwindow-fixer.exe' 2>/dev/null || true
  printf 'Fusion launcher: '
  pgrep -fc 'launch-fusion.sh' 2>/dev/null || true
  echo

  echo "== Selected safe config keys =="
  CFG="$HOME/.config/fusion360-linux/config"
  if [[ -r "$CFG" ]]; then
    grep -E '^(PROTON|STEAM_COMPAT_DATA_PATH|FUSION_ENABLE_TOOLWINDOW_FIXER|FUSION_FIX_BCP47LANGS|FUSION_USE_INTEL_VK_ICD|FUSION_WEBVIEW_NO_SANDBOX|FUSION_WEBVIEW_DISABLE_GPU)=' "$CFG" 2>/dev/null | sanitize_home || true
  else
    echo "config not found"
  fi
  echo

  echo "== Privacy note =="
  echo "No Fusion project files or Autodesk authentication logs were collected."
  echo "Review this file manually before posting it publicly."
} > "$OUT"

printf 'Diagnostics written to: %s\n' "$OUT"
printf 'Review the file before attaching it to a GitHub issue.\n'
