# Troubleshooting

## 1. Arch installer says `python3-tk` cannot be found

Arch uses the package name:

```bash
sudo pacman -S tk
```

The patcher changes an existing `src/install/distro/arch.txt` entry from
`python3-tk` to `tk` when that file is available.

## 2. Sign-in fails with `bcp47langs.dll.GetUserLanguages, aborting`

Typical terminal symptom:

```text
wine: Call from ... to unimplemented function bcp47langs.dll.GetUserLanguages, aborting
```

Two things matter:

### Correct DLL override separators

Independent Wine DLL override rules are separated with semicolons. For example:

```text
bcp47langs=;winhttp=b;icuuc,icuin,icudt=n,b
```

The ICU DLL names share one load-order rule, so commas are correct inside that
single rule.

### Persistent prefix override

Some Autodesk helper processes may not behave reliably with only inherited
environment overrides. This project also adds an empty Wine registry override
for `bcp47langs` under the Fusion prefix.

Verify it manually with the Wine binary next to the configured Proton build:

```bash
WINEPREFIX="$HOME/.fusion360-proton2/pfx" \
  /path/to/GE-Proton/files/bin/wine \
  reg query 'HKCU\Software\Wine\DllOverrides' /v bcp47langs
```

## 3. Hundreds of `fusion-toolwindow-fixer.exe` processes

Check:

```bash
pgrep -af 'fusion-toolwindow-fixer.exe'
```

The affected helper code can start the fixer twice and its health monitor can
restart it even when the feature should be disabled.

This project:

- sets `FUSION_ENABLE_TOOLWINDOW_FIXER=0`;
- removes the unscoped duplicate start;
- makes the health check honor the enable flag.

If a runaway instance already exists, stop the launcher and helper processes
before applying the fix:

```bash
pkill -f 'launch-fusion.sh' || true
pkill -f 'fusion-toolwindow-fixer.exe' || true
```

## 4. Browser callback opens an application chooser but Fusion does not resume

Check the expected handlers:

```bash
gio mime x-scheme-handler/adskidmgr
gio mime x-scheme-handler/adsk
```

The expected desktop ID is:

```text
fusion360-linux-fusion360-callback-handler.desktop
```

This project registers both schemes with `gio` instead of relying on
`xdg-mime`, because some KDE/Arch setups can have an `xdg-mime` path that fails
when `qtpaths` is missing.

## 5. Verify the callback path

Handler log:

```bash
tail -n 80 /tmp/fusion-callback-handler.log
```

Listener log:

```bash
tail -n 120 /tmp/fusion-browser-listener.log
```

A callback can legitimately appear as:

```text
adskidmgr:/login?code=...
```

Do not post the full callback URL publicly.

## 6. Check Fusion authentication logs

Find the newest Neutron Platform log:

```bash
LOGDIR="$HOME/.fusion360-proton2/pfx/drive_c/users/steamuser/AppData/Local/Autodesk/Neutron Platform/logs"
latest=$(command ls -1t "$LOGDIR"/AppLogFile*.log | head -n 1)
printf '%s\n' "$latest"
grep -niE 'IDSDK|login|auth|identity|token|failed|error' "$latest" | tail -n 100
```

Useful success lines:

```text
IDSDK immediatly returned success in sign-in dialog.
IDSDKAuth: idsdk_get_token returned IDSDK_E_SUCCESS
```

## 7. First-run/tutorial overlay is grey or behind the window

With the Toolwindow Fixer disabled, some Wine/KDE combinations may show a
first-run overlay with imperfect z-order. If the controls cannot be clicked,
try keyboard navigation:

```text
Tab     move focus
Space   toggle checkbox
Enter   activate button
Esc     dismiss overlay where supported
```

Once the initial tutorial is completed the overlay normally disappears.

## 8. Closing Fusion kills unrelated Proton applications

The original broad cleanup code may match generic names such as `wine`,
`proton`, `steam-runtime` or `node.exe`.

This project changes launcher cleanup to run `wineserver -k` only for the
configured Fusion `WINEPREFIX`.

That intentionally stops the Wine processes in the Fusion prefix without
terminating unrelated Proton prefixes.

## 9. NVIDIA / Vulkan warning from an unrelated implicit layer

A warning such as:

```text
Failed to find 'vkGetInstanceProcAddr' in layer ... liblsfg-vk-layer.so
```

may come from an unrelated Vulkan implicit layer. This project does not remove
or alter third-party Vulkan layers. Diagnose those separately if they cause an
actual rendering problem.
