"""Regression tests for upstream OAuth callback handling under sparse desktop environments.

Based on stonegray/fusion360-linux issue #5 (2026-10-29).
The fixture represents the pinned upstream handler's logging and request-writing
path. No real Autodesk credentials are used.
"""

import os
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest

import fusion360_arch_fix as fixes


UPSTREAM_CALLBACK_HANDLER = r'''#!/usr/bin/env bash
# fusion-callback-handler.sh: Fusion 360 Autodesk callback request writer.
set -euo pipefail

CALLBACK_DIR="/tmp/fusion360-callback-requests"
LOG_FILE="/tmp/fusion-callback-handler.log"

mkdir -p "$CALLBACK_DIR"

{
  echo "============================================================"
  echo "timestamp=$(date -Is)"
  echo "script=$0"
  echo "pid=$$"
  echo "ppid=$PPID"
  echo "pwd=$PWD"
  echo "argc=$#"

  argument_index=0
  for argument in "$@"; do
    printf 'argv[%d]=%q\n' "$argument_index" "$argument"
    echo "argv[${argument_index}]_len=${#argument}"
    echo "argv[${argument_index}]_first200=${argument:0:200}"
    echo "argv[${argument_index}]_last200=${argument: -200}"
    argument_index=$((argument_index + 1))
  done

  echo "--- env dump ---"
  echo "KDE_SESSION_VERSION=$KDE_SESSION_VERSION"
  echo "WAYLAND_DISPLAY=$WAYLAND_DISPLAY"
  echo "DISPLAY=$DISPLAY"
  echo "XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR"
  echo "DBUS_SESSION_BUS_ADDRESS=$DBUS_SESSION_BUS_ADDRESS"
  echo "============================================================"
  echo
} >> "$LOG_FILE" 2>&1

if [[ $# -lt 1 ]]; then
  echo "no callback url received" >> "$LOG_FILE"
  exit 0
fi

request_name="$(date +%s.%N).$$"
partial_file="$CALLBACK_DIR/$request_name.partial"
request_file="$CALLBACK_DIR/$request_name.request"

printf "%s\n" "$1" > "$partial_file"
mv "$partial_file" "$request_file"

echo "wrote_callback_request=$request_file" >> "$LOG_FILE"
exit 0
'''


class CallbackRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="fusion-callback-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.xdg = self.root / "xdg"
        self.xdg.mkdir()
        self.handler = self.root / "fusion-callback-handler.sh"
        patched, changed = fixes.patch_callback_privacy_text(UPSTREAM_CALLBACK_HANDLER)
        self.assertTrue(changed)
        self.assertEqual(fixes.patch_callback_privacy_text(patched), (patched, False))
        self.handler.write_text(patched)
        self.env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "HOME": str(self.root),
            "XDG_RUNTIME_DIR": str(self.xdg),
        }
        for name in ("KDE_SESSION_VERSION", "WAYLAND_DISPLAY", "DISPLAY",
                     "DBUS_SESSION_BUS_ADDRESS"):
            self.assertNotIn(name, self.env)

    def run_handler(self, *args):
        return subprocess.run(
            ["bash", str(self.handler), *args],
            env=self.env,
            cwd=self.root,
            text=True,
            capture_output=True,
            timeout=15,
            check=False,
        )

    def test_unset_optional_desktop_variables_do_not_drop_oauth_callback(self):
        fake_url = "adskidmgr://example.invalid/login?code=FAKE_TEST_CODE&state=FAKE_TEST_STATE"
        result = self.run_handler(fake_url)
        self.assertEqual(result.returncode, 0, result.stderr)
        runtime = self.xdg / "fusion360-linux"
        requests = list((runtime / "callback-requests").glob("*.request"))
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0].read_text(), fake_url + "\n")
        self.assertEqual(list((runtime / "callback-requests").glob("*.partial")), [])

        log_file = runtime / "callback-handler.log"
        log_text = log_file.read_text()
        self.assertIn("arguments_redacted=true", log_text)
        self.assertIn("KDE_SESSION_VERSION=", log_text)
        self.assertIn("DBUS_SESSION_BUS_ADDRESS=", log_text)
        self.assertNotIn("FAKE_TEST_CODE", log_text)
        self.assertNotIn("FAKE_TEST_STATE", log_text)
        self.assertNotIn(fake_url, log_text)

        for directory in (runtime, runtime / "callback-requests"):
            self.assertEqual(stat.S_IMODE(directory.stat().st_mode), 0o700)
        for private_file in (log_file, requests[0]):
            self.assertEqual(stat.S_IMODE(private_file.stat().st_mode), 0o600)

    def test_no_argument_does_not_create_callback_request(self):
        result = self.run_handler()
        self.assertEqual(result.returncode, 0, result.stderr)
        runtime = self.xdg / "fusion360-linux"
        self.assertEqual(list((runtime / "callback-requests").glob("*.request")), [])
        self.assertIn("no callback url received", (runtime / "callback-handler.log").read_text())


if __name__ == "__main__":
    unittest.main()
