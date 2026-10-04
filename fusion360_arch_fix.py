#!/usr/bin/env python3
"""Fusion 360 Linux Arch Fixes.

Small, idempotent patcher for stonegray/fusion360-linux installations on
Arch-family distributions. It applies only the fixes needed around launcher,
Autodesk Identity Manager callbacks, Wine DLL overrides, and prefix-scoped
cleanup. It does not distribute Autodesk software.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Dict, Iterable, List, Optional, Tuple

PROJECT_NAME = "Fusion 360 Linux Arch Fixes"
VERSION = "0.2.0"


def log(msg: str) -> None:
    print(msg)


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def warn(msg: str) -> None:
    print(f"[WARN] {msg}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")


def default_paths(home: Optional[Path] = None) -> Dict[str, Path]:
    home = home or Path.home()
    data_home = Path(os.path.expanduser(os.environ.get("XDG_DATA_HOME", str(home / ".local/share"))))
    config_home = Path(os.path.expanduser(os.environ.get("XDG_CONFIG_HOME", str(home / ".config"))))
    base = data_home / "fusion360-linux"
    return {
        "home": home,
        "base": base,
        "config": config_home / "fusion360-linux/config",
        "launcher": base / "runtime-scripts/launcher-functions.sh",
        "cleanup": base / "share/cleanup.fn",
        "process": base / "share/process.fn",
        "daemon": base / "share/daemon.fn",
        "browser": base / "runtime-scripts/fusion-browser.sh",
        "listener": base / "runtime-scripts/fusion-browser-listener.sh",
        "callback": base / "runtime-scripts/fusion-callback-handler.sh",
        "arch_deps": base / "src/install/distro/arch.txt",
        "callback_desktop": data_home
        / "applications/fusion360-linux/fusion360-callback-handler.desktop",
        "backup_root": base / "backup-arch-fixes",
    }


def parse_config_text(text: str) -> Dict[str, str]:
    values: Dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def set_config_values(text: str, updates: Dict[str, str]) -> str:
    lines = text.splitlines()
    seen = set()
    out: List[str] = []
    for line in lines:
        if "=" in line and not line.lstrip().startswith("#"):
            key = line.split("=", 1)[0].strip()
            if key in updates:
                if key not in seen:
                    out.append(f"{key}={updates[key]}")
                    seen.add(key)
                continue
        out.append(line)
    for key, value in updates.items():
        if key not in seen:
            out.append(f"{key}={value}")
    return "\n".join(out).rstrip() + "\n"


def patch_launcher_text(text: str) -> Tuple[str, bool]:
    original = text
    # Separate independent override rules with ';'. Commas are for DLLs that
    # share the same load order, e.g. icuuc,icuin,icudt=n,b.
    text = text.replace(
        "${dll_overrides:+$dll_overrides,}winhttp=b",
        "${dll_overrides:+$dll_overrides;}winhttp=b",
    )
    text = text.replace(
        "${dll_overrides:+$dll_overrides,}icuuc,icuin,icudt=n,b",
        "${dll_overrides:+$dll_overrides;}icuuc,icuin,icudt=n,b",
    )
    return text, text != original


def _line_indent_at(text: str, pos: int) -> str:
    line_start = text.rfind("\n", 0, pos) + 1
    prefix = text[line_start:pos]
    return re.match(r"[ \t]*", prefix).group(0)  # type: ignore[union-attr]


def patch_cleanup_text(text: str) -> Tuple[str, bool]:
    marker = "# Stop Wine only for the Fusion prefix."
    if marker in text:
        return text, False

    start_token = "# Kill Fusion/Wine/Proton processes"
    end_token = "# Remove PID file directory"
    start = text.find(start_token)
    if start < 0:
        raise ValueError("cleanup.fn: kill-process section not found")
    end = text.find(end_token, start)
    if end < 0:
        raise ValueError("cleanup.fn: end of kill-process section not found")

    line_start = text.rfind("\n", 0, start) + 1
    end_line_start = text.rfind("\n", 0, end) + 1
    indent = _line_indent_at(text, start)

    block = (
        f"{indent}# Stop Wine only for the Fusion prefix.\n"
        f"{indent}# Avoid kill_fusion_processes because it can match unrelated Proton/Wine apps.\n"
        f"{indent}if [[ -n \"${{PROTON:-}}\" && -n \"${{STEAM_COMPAT_DATA_PATH:-}}\" ]]; then\n"
        f"{indent}  local proton_dir wineserver_bin fusion_prefix\n"
        f"{indent}  proton_dir=\"${{PROTON%/*}}\"\n"
        f"{indent}  wineserver_bin=\"$proton_dir/files/bin/wineserver\"\n"
        f"{indent}  fusion_prefix=\"$STEAM_COMPAT_DATA_PATH/pfx\"\n"
        f"{indent}\n"
        f"{indent}  if [[ -x \"$wineserver_bin\" ]]; then\n"
        f"{indent}    WINEPREFIX=\"$fusion_prefix\" \"$wineserver_bin\" -k 2>/dev/null || true\n"
        f"{indent}  fi\n"
        f"{indent}fi\n\n"
    )
    return text[:line_start] + block + text[end_line_start:], True


def patch_daemon_text(text: str) -> Tuple[str, bool]:
    original = text

    duplicate_spawn = '    nohup "$wine_bin" "$FUSION_TOOLWINDOW_FIXER" &>/dev/null &\n'
    if duplicate_spawn in text:
        # Keep the setsid/WINEPREFIX launch, remove the unscoped duplicate.
        text = text.replace(duplicate_spawn, "", 1)

    text = re.sub(
        r'(?m)^(\s*)if ! daemon_check_running "toolwindow-fixer" && \[\[ -x "\$FUSION_TOOLWINDOW_FIXER" \]\]; then$',
        r'\1if _is_enabled "$FUSION_ENABLE_TOOLWINDOW_FIXER" && ! daemon_check_running "toolwindow-fixer" && [[ -x "$FUSION_TOOLWINDOW_FIXER" ]]; then',
        text,
        count=1,
    )
    return text, text != original


def patch_arch_deps_text(text: str) -> Tuple[str, bool]:
    lines = text.splitlines()
    changed = False
    out = []
    stripped = [line.strip() for line in lines]
    for line in lines:
        if line.strip() == "python3-tk":
            prefix = line[: len(line) - len(line.lstrip())]
            out.append(prefix + "tk")
            changed = True
        else:
            out.append(line)
    # gio is used for reliable Autodesk callback registration on Arch.
    if "glib2" not in stripped:
        out.append("glib2")
        changed = True
    suffix = "\n" if text.endswith("\n") else ""
    return "\n".join(out) + suffix, changed


def patch_process_text(text: str) -> Tuple[str, bool]:
    marker = "# Fusion Arch Fixes: prefix-scoped process shutdown"
    if marker in text:
        return text, False

    start = text.find("kill_fusion_processes() {")
    end_marker = "# ── Installer-specific kill"
    end = text.find(end_marker, start)
    if start < 0 or end < 0:
        raise ValueError("process.fn: kill_fusion_processes section not found")

    line_start = text.rfind("\n", 0, start) + 1
    end_line_start = text.rfind("\n", 0, end) + 1
    function = r'''# Fusion Arch Fixes: prefix-scoped process shutdown
kill_fusion_processes() {
  local pfx_root="${PFX_DIR:-${STEAM_COMPAT_DATA_PATH:-$HOME/.fusion360-proton2}}"
  local prefix="$pfx_root/pfx"
  local wineserver_bin=""

  # Prefer the exact Proton configured for Fusion.
  if [[ -n "${PROTON:-}" ]]; then
    local proton_dir="${PROTON%/*}"
    if [[ -x "$proton_dir/files/bin/wineserver" ]]; then
      wineserver_bin="$proton_dir/files/bin/wineserver"
    fi
  fi

  # During installation PROTON may not be exported yet.  Resolve the Proton
  # installed in Fusion's compatibility-tools directory without touching
  # unrelated Wine/Proton prefixes.
  if [[ -z "$wineserver_bin" && -n "${COMPAT_DIR:-}" && -d "$COMPAT_DIR" ]]; then
    wineserver_bin="$(find "$COMPAT_DIR" -path '*/files/bin/wineserver' -type f -print 2>/dev/null | sort | tail -n 1 || true)"
  fi

  if [[ -n "$wineserver_bin" && -x "$wineserver_bin" && -d "$prefix" ]]; then
    WINEPREFIX="$prefix" "$wineserver_bin" -k 2>/dev/null || true
    sleep 0.5
    return 0
  fi

  # Last-resort fallback: only the wineserver lock belonging to this prefix.
  local ws="$prefix/.wineserver.lock"
  if [[ -f "$ws" ]]; then
    local ws_pid
    ws_pid="$(head -1 "$ws" 2>/dev/null || true)"
    if [[ "$ws_pid" =~ ^[0-9]+$ ]]; then
      kill "$ws_pid" 2>/dev/null || true
    fi
  fi
  return 0
}

'''
    return text[:line_start] + function + text[end_line_start:], True


def _secure_shell_log_and_dir(text: str, dir_var: str) -> str:
    if "umask 077" not in text:
        text = text.replace("set -euo pipefail\n", "set -euo pipefail\numask 077\n", 1)

    mkdir_line = f'mkdir -p "${dir_var}"'
    secure_block = (
        mkdir_line
        + f'\nchmod 700 "${dir_var}" 2>/dev/null || true'
        + '\ntouch "$LOG_FILE"'
        + '\nchmod 600 "$LOG_FILE" 2>/dev/null || true'
    )
    if f'chmod 700 "${dir_var}"' not in text and mkdir_line in text:
        text = text.replace(mkdir_line, secure_block, 1)
    return text


def patch_browser_writer_privacy_text(text: str) -> Tuple[str, bool]:
    original = text
    text = text.replace(
        'REQUEST_DIR="/tmp/fusion360-browser-requests"\n'
        'LOG_FILE="/tmp/fusion-browser-bridge.log"',
        '''if [[ -n "${XDG_RUNTIME_DIR:-}" ]]; then
  RUNTIME_BASE="$XDG_RUNTIME_DIR/fusion360-linux"
else
  RUNTIME_BASE="/tmp/fusion360-linux-$UID"
fi
if [[ -e "$RUNTIME_BASE" && ( -L "$RUNTIME_BASE" || ! -O "$RUNTIME_BASE" ) ]]; then
  echo "unsafe Fusion runtime directory: $RUNTIME_BASE" >&2
  exit 1
fi
mkdir -p "$RUNTIME_BASE"
if [[ -L "$RUNTIME_BASE" || ! -O "$RUNTIME_BASE" ]]; then
  echo "unsafe Fusion runtime directory after creation: $RUNTIME_BASE" >&2
  exit 1
fi
chmod 700 "$RUNTIME_BASE"
REQUEST_DIR="$RUNTIME_BASE/browser-requests"
LOG_FILE="$RUNTIME_BASE/browser-bridge.log"''',
    )
    text = _secure_shell_log_and_dir(text, "REQUEST_DIR")

    if '  echo "arguments_redacted=true"' not in text:
        start = text.find("  argument_index=0\n")
        end_token = '  echo "--- env dump ---"'
        end = text.find(end_token, start)
        if start < 0 or end < 0:
            raise ValueError("browser bridge: argument logging section not found")
        replacement = '''  echo "arguments_redacted=true"
  argument_index=0
  for argument in "$@"; do
    echo "argv[${argument_index}]=[redacted]"
    echo "argv[${argument_index}]_len=${#argument}"
    argument_index=$((argument_index + 1))
  done

'''
        text = text[:start] + replacement + text[end:]
    return text, text != original


def patch_listener_privacy_text(text: str) -> Tuple[str, bool]:
    original = text
    text = text.replace(
        'BROWSER_REQUEST_DIR="/tmp/fusion360-browser-requests"\n'
        'BROWSER_PROCESSED_DIR="/tmp/fusion360-browser-processed"\n'
        'CALLBACK_REQUEST_DIR="/tmp/fusion360-callback-requests"\n'
        'CALLBACK_PROCESSED_DIR="/tmp/fusion360-callback-processed"\n'
        'LOG_FILE="/tmp/fusion-browser-listener.log"',
        '''if [[ -n "${XDG_RUNTIME_DIR:-}" ]]; then
  RUNTIME_BASE="$XDG_RUNTIME_DIR/fusion360-linux"
else
  RUNTIME_BASE="/tmp/fusion360-linux-$UID"
fi
if [[ -e "$RUNTIME_BASE" && ( -L "$RUNTIME_BASE" || ! -O "$RUNTIME_BASE" ) ]]; then
  echo "unsafe Fusion runtime directory: $RUNTIME_BASE" >&2
  exit 1
fi
mkdir -p "$RUNTIME_BASE"
if [[ -L "$RUNTIME_BASE" || ! -O "$RUNTIME_BASE" ]]; then
  echo "unsafe Fusion runtime directory after creation: $RUNTIME_BASE" >&2
  exit 1
fi
chmod 700 "$RUNTIME_BASE"
BROWSER_REQUEST_DIR="$RUNTIME_BASE/browser-requests"
BROWSER_PROCESSED_DIR="$RUNTIME_BASE/browser-processed"
CALLBACK_REQUEST_DIR="$RUNTIME_BASE/callback-requests"
CALLBACK_PROCESSED_DIR="$RUNTIME_BASE/callback-processed"
LOG_FILE="$RUNTIME_BASE/browser-listener.log"''',
    )
    if "umask 077" not in text:
        text = text.replace("set -euo pipefail\n", "set -euo pipefail\numask 077\n", 1)

    dirs = [
        "BROWSER_REQUEST_DIR",
        "BROWSER_PROCESSED_DIR",
        "CALLBACK_REQUEST_DIR",
        "CALLBACK_PROCESSED_DIR",
    ]
    mkdir_block = (
        'mkdir -p "$BROWSER_REQUEST_DIR"\n'
        'mkdir -p "$BROWSER_PROCESSED_DIR"\n'
        'mkdir -p "$CALLBACK_REQUEST_DIR"\n'
        'mkdir -p "$CALLBACK_PROCESSED_DIR"'
    )
    if 'chmod 700 "$BROWSER_REQUEST_DIR"' not in text and mkdir_block in text:
        secure = mkdir_block + "\n" + "\n".join(
            f'chmod 700 "${name}" 2>/dev/null || true' for name in dirs
        ) + '\ntouch "$LOG_FILE"\nchmod 600 "$LOG_FILE" 2>/dev/null || true'
        text = text.replace(mkdir_block, secure, 1)

    text = text.replace(
        "    printf 'url=%q\\n' \"$url\"\n"
        '    echo "url_first300=${url:0:300}"\n'
        '    echo "url_last300=${url: -300}"\n',
        '    echo "url=[redacted query; len=${#url}]"\n',
    )
    text = text.replace(
        '    echo "url=$url"\n',
        '    echo "url=[redacted query; len=${#url}]"\n',
    )
    text = text.replace(
        "    printf 'callback_url=%q\\n' \"$callback_url\"\n",
        '    echo "callback_url=[redacted; len=${#callback_url}]"\n',
    )
    # Preserve empty processed markers, but scrub sensitive URL contents
    # before moving requests into processed directories.
    browser_start = text.find("open_browser_url() {")
    callback_start = text.find("send_callback_to_identity_manager() {")
    if browser_start >= 0 and callback_start > browser_start:
        browser_section = text[browser_start:callback_start]
        browser_section = browser_section.replace(
            '{ mv "$request_file" "$processed_file"; return 0; }',
            '{ : > "$request_file"; mv "$request_file" "$processed_file"; return 0; }',
        )
        browser_section = browser_section.replace(
            '  mv "$request_file" "$processed_file"\n',
            '  : > "$request_file"\n  mv "$request_file" "$processed_file"\n',
        )
        text = text[:browser_start] + browser_section + text[callback_start:]

    callback_start = text.find("send_callback_to_identity_manager() {")
    process_start = text.find("process_browser_requests() {", callback_start)
    if callback_start >= 0 and process_start > callback_start:
        callback_section = text[callback_start:process_start]
        callback_section = callback_section.replace(
            '    mv "$request_file" "$processed_file"\n',
            '    : > "$request_file"\n    mv "$request_file" "$processed_file"\n',
        )
        callback_section = callback_section.replace(
            '  mv "$request_file" "$processed_file"\n',
            '  : > "$request_file"\n  mv "$request_file" "$processed_file"\n',
        )
        text = text[:callback_start] + callback_section + text[process_start:]

    return text, text != original


def patch_callback_privacy_text(text: str) -> Tuple[str, bool]:
    original = text
    text = text.replace(
        'CALLBACK_DIR="/tmp/fusion360-callback-requests"\n'
        'LOG_FILE="/tmp/fusion-callback-handler.log"',
        '''if [[ -n "${XDG_RUNTIME_DIR:-}" ]]; then
  RUNTIME_BASE="$XDG_RUNTIME_DIR/fusion360-linux"
else
  RUNTIME_BASE="/tmp/fusion360-linux-$UID"
fi
if [[ -e "$RUNTIME_BASE" && ( -L "$RUNTIME_BASE" || ! -O "$RUNTIME_BASE" ) ]]; then
  echo "unsafe Fusion runtime directory: $RUNTIME_BASE" >&2
  exit 1
fi
mkdir -p "$RUNTIME_BASE"
if [[ -L "$RUNTIME_BASE" || ! -O "$RUNTIME_BASE" ]]; then
  echo "unsafe Fusion runtime directory after creation: $RUNTIME_BASE" >&2
  exit 1
fi
chmod 700 "$RUNTIME_BASE"
CALLBACK_DIR="$RUNTIME_BASE/callback-requests"
LOG_FILE="$RUNTIME_BASE/callback-handler.log"''',
    )
    text = _secure_shell_log_and_dir(text, "CALLBACK_DIR")

    text = text.replace(
        'echo "KDE_SESSION_VERSION=$KDE_SESSION_VERSION"',
        'echo "KDE_SESSION_VERSION=${KDE_SESSION_VERSION:-}"',
    )
    text = text.replace(
        'echo "WAYLAND_DISPLAY=$WAYLAND_DISPLAY"',
        'echo "WAYLAND_DISPLAY=${WAYLAND_DISPLAY:-}"',
    )
    text = text.replace(
        'echo "DISPLAY=$DISPLAY"',
        'echo "DISPLAY=${DISPLAY:-}"',
    )
    text = text.replace(
        'echo "XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR"',
        'echo "XDG_RUNTIME_DIR=${XDG_RUNTIME_DIR:-}"',
    )
    text = text.replace(
        'echo "DBUS_SESSION_BUS_ADDRESS=$DBUS_SESSION_BUS_ADDRESS"',
        'echo "DBUS_SESSION_BUS_ADDRESS=${DBUS_SESSION_BUS_ADDRESS:-}"',
    )

    if '  echo "arguments_redacted=true"' not in text:
        start = text.find("  argument_index=0\n")
        end_token = '  echo "--- env dump ---"'
        end = text.find(end_token, start)
        if start < 0 or end < 0:
            raise ValueError("callback handler: argument logging section not found")

        replacement = '''  echo "arguments_redacted=true"
  argument_index=0
  for argument in "$@"; do
    echo "argv[${argument_index}]=[redacted]"
    echo "argv[${argument_index}]_len=${#argument}"
    argument_index=$((argument_index + 1))
  done

'''
        text = text[:start] + replacement + text[end:]
    return text, text != original


def patch_upstream_install_text(text: str) -> Tuple[str, bool]:
    """Make upstream's manual --kill mode prefix-scoped too."""
    marker = "# Fusion Arch Fixes: safe --kill"
    if marker in text:
        return text, False

    start = text.find('if [[ "${1:-}" == "--kill" ]]; then')
    end_token = 'MODE="${1:-}"'
    end = text.find(end_token, start)
    if start < 0 or end < 0:
        raise ValueError("upstream install.sh: --kill section not found")

    line_start = text.rfind("\n", 0, start) + 1
    replacement = r'''# Fusion Arch Fixes: safe --kill
if [[ "${1:-}" == "--kill" ]]; then
  source "$SCRIPT_DIR/src/install/00-common.sh"
  echo "Stopping Wine processes only in the Fusion 360 prefix..."
  kill_fusion_processes || true
  exit 0
fi


'''
    return text[:line_start] + replacement + text[end:], True


def write_if_changed(path: Path, new_text: str) -> bool:
    old = path.read_text()
    if old == new_text:
        return False
    path.write_text(new_text)
    return True


def backup_files(paths: Dict[str, Path], files: Iterable[Path]) -> Path:
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup = paths["backup_root"] / stamp
    backup.mkdir(mode=0o700, parents=True, exist_ok=False)

    manifest = {"created": stamp, "version": VERSION, "files": []}
    for i, path in enumerate(files):
        record = {"path": str(path), "existed": path.exists(), "backup": None}
        if path.exists():
            name = f"{i:02d}-{path.name}"
            target = backup / name
            shutil.copy2(path, target)
            record["backup"] = name
        manifest["files"].append(record)

    (backup / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return backup


def latest_backup(paths: Dict[str, Path]) -> Optional[Path]:
    root = paths["backup_root"]
    if not root.exists():
        return None
    candidates = sorted((p for p in root.iterdir() if p.is_dir()), reverse=True)
    return candidates[0] if candidates else None


def restore_backup(backup: Path) -> None:
    manifest_path = backup / "manifest.json"
    if not manifest_path.exists():
        raise RuntimeError(f"No manifest.json in {backup}")
    manifest = json.loads(manifest_path.read_text())
    for rec in manifest.get("files", []):
        path = Path(rec["path"])
        if rec.get("existed"):
            src = backup / rec["backup"]
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, path)
            ok(f"restored {path}")
        elif path.exists():
            path.unlink()
            ok(f"removed {path} (did not exist before backup)")


def run_quiet(args: List[str], env: Optional[Dict[str, str]] = None) -> subprocess.CompletedProcess:
    return subprocess.run(args, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def find_wine(config: Dict[str, str]) -> Optional[Path]:
    proton = config.get("PROTON", "")
    if not proton:
        return None
    proton_path = Path(os.path.expanduser(proton))
    for candidate in [
        proton_path.parent / "files/bin/wine",
        proton_path.parent / "files/bin/wine64",
    ]:
        if candidate.exists() and os.access(candidate, os.X_OK):
            return candidate
    return None


def apply_registry_override(paths: Dict[str, Path], config: Dict[str, str]) -> bool:
    wine = find_wine(config)
    if wine is None:
        warn("Wine binary not found next to configured Proton; skipped registry override")
        return False
    data_path = Path(os.path.expanduser(config.get("STEAM_COMPAT_DATA_PATH", str(paths["home"] / ".fusion360-proton2"))))
    env = os.environ.copy()
    env["WINEPREFIX"] = str(data_path / "pfx")
    result = run_quiet(
        [
            str(wine),
            "reg",
            "add",
            r"HKCU\Software\Wine\DllOverrides",
            "/v",
            "bcp47langs",
            "/t",
            "REG_SZ",
            "/d",
            "",
            "/f",
        ],
        env=env,
    )
    if result.returncode == 0:
        ok("persistent Wine override: bcp47langs disabled")
        return True
    warn("could not set bcp47langs registry override")
    return False


def register_callback_handlers(paths: Dict[str, Path]) -> bool:
    gio = shutil.which("gio")
    desktop_id = "fusion360-linux-fusion360-callback-handler.desktop"
    if not gio:
        warn("gio not found; callback MIME registration skipped")
        return False
    if not paths["callback_desktop"].exists():
        warn(f"callback desktop file not found yet: {paths['callback_desktop']}")
        return False
    good = True
    for scheme in ["x-scheme-handler/adskidmgr", "x-scheme-handler/adsk"]:
        result = run_quiet([gio, "mime", scheme, desktop_id])
        good = good and result.returncode == 0
    if good:
        ok("Autodesk callback handlers registered via gio")
    else:
        warn("one or more callback handler registrations failed")
    return good


def syntax_check(files: Iterable[Path]) -> bool:
    good = True
    for path in files:
        if not path.exists():
            continue
        result = run_quiet(["bash", "-n", str(path)])
        if result.returncode != 0:
            fail(f"bash syntax: {path}\n{result.stderr.strip()}")
            good = False
    return good


def apply(paths: Dict[str, Path]) -> int:
    required = [
        paths["config"], paths["launcher"], paths["cleanup"], paths["process"],
        paths["daemon"], paths["browser"], paths["listener"], paths["callback"],
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        fail("fusion360-linux installation not found or incomplete:\n  " + "\n  ".join(missing))
        return 2

    # Validate every text transform before modifying the installed runtime.
    # This makes new/upstream layouts fail closed instead of leaving a half-patched tree.
    try:
        transformed: Dict[Path, str] = {
            paths["launcher"]: patch_launcher_text(paths["launcher"].read_text())[0],
            paths["cleanup"]: patch_cleanup_text(paths["cleanup"].read_text())[0],
            paths["process"]: patch_process_text(paths["process"].read_text())[0],
            paths["daemon"]: patch_daemon_text(paths["daemon"].read_text())[0],
            paths["browser"]: patch_browser_writer_privacy_text(paths["browser"].read_text())[0],
            paths["listener"]: patch_listener_privacy_text(paths["listener"].read_text())[0],
            paths["callback"]: patch_callback_privacy_text(paths["callback"].read_text())[0],
        }
        if paths["arch_deps"].exists():
            transformed[paths["arch_deps"]] = patch_arch_deps_text(paths["arch_deps"].read_text())[0]
    except Exception as exc:
        fail(f"preflight patch validation failed; no files were changed: {exc}")
        return 3

    backup = backup_files(
        paths,
        [
            paths["config"], paths["launcher"], paths["cleanup"], paths["process"],
            paths["daemon"], paths["browser"], paths["listener"], paths["callback"],
            paths["arch_deps"],
        ],
    )
    log(f"Backup: {backup}")

    try:
        config_updates = {
            "FUSION_ENABLE_TOOLWINDOW_FIXER": "0",
            "FUSION_FIX_BCP47LANGS": "1",
            "FUSION_USE_INTEL_VK_ICD": "0",
            "FUSION_WEBVIEW_NO_SANDBOX": "1",
            "FUSION_WEBVIEW_DISABLE_GPU": "0",
        }
        config_text = set_config_values(paths["config"].read_text(), config_updates)
        write_if_changed(paths["config"], config_text)
        ok("launcher configuration")

        labels = {
            paths["launcher"]: "WINEDLLOVERRIDES separators",
            paths["cleanup"]: "prefix-scoped cleanup",
            paths["process"]: "prefix-scoped process shutdown",
            paths["daemon"]: "toolwindow fixer safeguards",
            paths["browser"]: "browser request privacy and private runtime files",
            paths["listener"]: "browser/callback privacy and private runtime directories",
            paths["callback"]: "callback privacy and desktop-session portability",
            paths["arch_deps"]: "Arch dependency compatibility",
        }
        for path, new_text in transformed.items():
            write_if_changed(path, new_text)
            ok(labels[path])

        if paths["callback"].exists():
            mode = paths["callback"].stat().st_mode
            paths["callback"].chmod(mode | 0o111)

        shell_files = [
            paths["launcher"], paths["cleanup"], paths["process"], paths["daemon"],
            paths["browser"], paths["listener"], paths["callback"],
        ]
        if not syntax_check(shell_files):
            raise RuntimeError("patched shell syntax check failed")

    except Exception as exc:
        fail(f"patch application failed: {exc}")
        warn("restoring file backup automatically")
        try:
            restore_backup(backup)
            ok("file rollback completed")
        except Exception as restore_exc:
            fail(f"automatic rollback also failed: {restore_exc}")
        return 3

    register_callback_handlers(paths)
    cfg = parse_config_text(paths["config"].read_text())
    apply_registry_override(paths, cfg)

    ok("bash syntax check")
    log("\nApplied successfully.")
    log("Run: python3 fusion360_arch_fix.py check")
    return 0

def check(paths: Dict[str, Path]) -> int:
    checks: List[Tuple[str, bool, bool]] = []  # name, pass, essential

    for key in ["config", "launcher", "cleanup", "process", "daemon", "browser", "listener", "callback"]:
        checks.append((f"exists: {paths[key]}", paths[key].exists(), True))
    if not all(
        p.exists()
        for p in [
            paths["config"], paths["launcher"], paths["cleanup"], paths["process"],
            paths["daemon"], paths["browser"], paths["listener"], paths["callback"],
        ]
    ):
        for name, status, _ in checks:
            (ok if status else fail)(name)
        return 2

    cfg = parse_config_text(paths["config"].read_text())
    expected_cfg = {
        "FUSION_ENABLE_TOOLWINDOW_FIXER": "0",
        "FUSION_FIX_BCP47LANGS": "1",
        "FUSION_USE_INTEL_VK_ICD": "0",
        "FUSION_WEBVIEW_NO_SANDBOX": "1",
        "FUSION_WEBVIEW_DISABLE_GPU": "0",
    }
    for key, value in expected_cfg.items():
        checks.append((f"config {key}={value}", cfg.get(key) == value, True))

    launcher = paths["launcher"].read_text()
    checks.append(("WINEDLLOVERRIDES winhttp uses ';' separator", "${dll_overrides:+$dll_overrides;}winhttp=b" in launcher, True))
    checks.append(("WINEDLLOVERRIDES ICU uses ';' separator", "${dll_overrides:+$dll_overrides;}icuuc,icuin,icudt=n,b" in launcher, True))

    cleanup = paths["cleanup"].read_text()
    checks.append(("cleanup is prefix-scoped", "# Stop Wine only for the Fusion prefix." in cleanup, True))
    checks.append(("cleanup does not call broad kill_fusion_processes", "kill_fusion_processes || true" not in cleanup, True))

    process = paths["process"].read_text()
    checks.append(("process shutdown is prefix-scoped", "# Fusion Arch Fixes: prefix-scoped process shutdown" in process, True))

    daemon = paths["daemon"].read_text()
    checks.append(("unscoped duplicate toolwindow spawn removed", 'nohup "$wine_bin" "$FUSION_TOOLWINDOW_FIXER" &>/dev/null &' not in daemon, True))
    checks.append(("toolwindow health restart honors enable flag", '_is_enabled "$FUSION_ENABLE_TOOLWINDOW_FIXER" && ! daemon_check_running "toolwindow-fixer"' in daemon, True))

    browser = paths["browser"].read_text()
    checks.append(("browser bridge redacts URL arguments", "arguments_redacted=true" in browser and "first200=" not in browser, True))
    checks.append(("browser bridge uses private files", "umask 077" in browser and 'chmod 700 "$REQUEST_DIR"' in browser, True))
    checks.append(("browser bridge moved off shared /tmp paths", 'REQUEST_DIR="/tmp/fusion360-browser-requests"' not in browser and "RUNTIME_BASE=" in browser, True))

    listener = paths["listener"].read_text()
    checks.append(("listener does not log raw callback URLs", "printf 'callback_url=%q" not in listener, True))
    checks.append(("listener does not log browser URL query samples", "url_first300=" not in listener and "url_last300=" not in listener, True))
    checks.append(("listener bridge directories are private", "umask 077" in listener and 'chmod 700 "$CALLBACK_REQUEST_DIR"' in listener, True))
    checks.append(("listener moved off shared /tmp paths", 'CALLBACK_REQUEST_DIR="/tmp/fusion360-callback-requests"' not in listener and "RUNTIME_BASE=" in listener, True))
    checks.append(("processed auth requests are scrubbed", ': > "$request_file"' in listener, True))

    callback = paths["callback"].read_text()
    checks.append(("callback handler redacts arguments", "arguments_redacted=true" in callback and "printf 'argv[%d]=%q" not in callback, True))
    checks.append(("callback handler uses private files", "umask 077" in callback and 'chmod 700 "$CALLBACK_DIR"' in callback, True))
    checks.append(("callback handler moved off shared /tmp paths", 'CALLBACK_DIR="/tmp/fusion360-callback-requests"' not in callback and "RUNTIME_BASE=" in callback, True))

    if paths["arch_deps"].exists():
        arch = paths["arch_deps"].read_text().splitlines()
        checks.append(("Arch dependency uses tk, not python3-tk", "python3-tk" not in [x.strip() for x in arch], False))

    shell_ok = syntax_check([
        paths["launcher"], paths["cleanup"], paths["process"], paths["daemon"],
        paths["browser"], paths["listener"], paths["callback"],
    ])
    checks.append(("bash syntax", shell_ok, True))

    # MIME association check via gio (locale independent enough: search desktop id in output).
    gio = shutil.which("gio")
    desktop_id = "fusion360-linux-fusion360-callback-handler.desktop"
    if gio:
        for scheme in ["x-scheme-handler/adskidmgr", "x-scheme-handler/adsk"]:
            r = run_quiet([gio, "mime", scheme])
            checks.append((f"callback {scheme}", r.returncode == 0 and desktop_id in (r.stdout + r.stderr), True))
    else:
        checks.append(("gio available for callback registration", False, False))

    # Registry check.
    wine = find_wine(cfg)
    if wine:
        data_path = Path(os.path.expanduser(cfg.get("STEAM_COMPAT_DATA_PATH", str(paths["home"] / ".fusion360-proton2"))))
        env = os.environ.copy()
        env["WINEPREFIX"] = str(data_path / "pfx")
        r = run_quiet([str(wine), "reg", "query", r"HKCU\Software\Wine\DllOverrides", "/v", "bcp47langs"], env=env)
        checks.append(("Wine registry bcp47langs override exists", r.returncode == 0 and "bcp47langs" in (r.stdout + r.stderr), True))
    else:
        checks.append(("Wine binary found for registry check", False, False))

    essential_failed = False
    log(f"{PROJECT_NAME} {VERSION} check\n")
    for name, status, essential in checks:
        if status:
            ok(name)
        elif essential:
            fail(name)
            essential_failed = True
        else:
            warn(name)

    return 1 if essential_failed else 0


def list_backups(paths: Dict[str, Path]) -> int:
    root = paths["backup_root"]
    if not root.exists():
        log("No backups yet.")
        return 0
    for p in sorted((x for x in root.iterdir() if x.is_dir()), reverse=True):
        print(p)
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=PROJECT_NAME)
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("apply", help="back up and apply all tested Arch/CachyOS fixes")
    sub.add_parser("check", help="verify the current installation")
    sub.add_parser("backups", help="list backups made by this tool")
    restore_p = sub.add_parser("restore", help="restore a backup (default: latest)")
    restore_p.add_argument("backup", nargs="?", help="backup directory; latest when omitted")

    args = parser.parse_args(argv)
    paths = default_paths()

    if args.command == "apply":
        return apply(paths)
    if args.command == "check":
        return check(paths)
    if args.command == "backups":
        return list_backups(paths)
    if args.command == "restore":
        backup = Path(args.backup).expanduser() if args.backup else latest_backup(paths)
        if backup is None:
            fail("no backups found")
            return 2
        restore_backup(backup)
        log("File restore complete. MIME associations and the Wine registry override are intentionally left unchanged.")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
