# Fusion 360 Linux Arch Fixes

[![tests](https://github.com/terrakot2001/fusion360-linux-arch-fixes/actions/workflows/tests.yml/badge.svg)](https://github.com/terrakot2001/fusion360-linux-arch-fixes/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform: Arch Linux](https://img.shields.io/badge/platform-Arch%20Linux-1793D1.svg)](https://archlinux.org/)

[Polski README](README_PL.md)

Unofficial compatibility fixes for running **Autodesk Fusion 360** with
[`stonegray/fusion360-linux`](https://github.com/stonegray/fusion360-linux) on
**Arch Linux and Arch-based distributions** such as CachyOS, EndeavourOS and
Manjaro.

This project does **not** distribute Autodesk Fusion, Autodesk binaries, Wine,
or Proton. It only patches launcher/helper scripts in an existing
`fusion360-linux` installation.

> Tested on Arch/CachyOS, KDE Plasma 6 on Wayland, NVIDIA GPU, GE-Proton 10-32,
> with Fusion 360 in October 2026.

## What this fixes

The patcher applies the set of fixes that were required in a real Arch/CachyOS
installation:

- changes the Arch dependency `python3-tk` to the correct Arch package `tk`
  when the dependency file is present;
- fixes malformed `WINEDLLOVERRIDES` composition by using `;` between
  independent rules;
- disables Wine's `bcp47langs` stub persistently for the Fusion prefix, which
  avoids `bcp47langs.dll.GetUserLanguages, aborting` in Autodesk Identity
  Manager;
- disables the currently problematic Toolwindow Fixer by default;
- removes the duplicate Toolwindow Fixer spawn and makes its health monitor
  respect the enable/disable setting;
- replaces broad Wine/Proton cleanup with prefix-scoped `wineserver -k`, so
  closing Fusion does not kill unrelated Proton/Wine applications;
- registers Autodesk `adsk://` and `adskidmgr://` callback handlers with `gio`,
  which works around broken `xdg-mime` setups such as missing `qtpaths`;
- creates timestamped backups before changing files;
- verifies modified shell scripts with `bash -n`.

## Requirements

You need an existing installation of `stonegray/fusion360-linux`, normally at:

```text
~/.local/share/fusion360-linux
```

and its configuration file at:

```text
~/.config/fusion360-linux/config
```

You also need:

- Python 3
- Bash
- `gio` from GLib for callback registration
- a working Proton configuration in `fusion360-linux`

## Quick start

Clone this repository and run:

```bash
git clone https://github.com/terrakot2001/fusion360-linux-arch-fixes.git
cd fusion360-linux-arch-fixes
bash install.sh
```

Then start Fusion normally:

```bash
~/.local/share/fusion360-linux/launch-fusion.sh
```

The patcher is idempotent: running it again should not duplicate changes.

## Check the installation

```bash
bash check.sh
```

or:

```bash
python3 fusion360_arch_fix.py check
```

A healthy installation should report `[OK]` for the essential checks.

For a privacy-conscious support report, generate diagnostics locally:

```bash
bash scripts/collect-diagnostics.sh
```

The script does **not** upload anything. Review the generated file before
attaching it to an issue.

## Backups and rollback

Every `apply` creates a timestamped backup under:

```text
~/.local/share/fusion360-linux/backup-arch-fixes/
```

List backups:

```bash
python3 fusion360_arch_fix.py backups
```

Restore the latest backup:

```bash
python3 fusion360_arch_fix.py restore
```

Or restore a specific backup:

```bash
python3 fusion360_arch_fix.py restore ~/.local/share/fusion360-linux/backup-arch-fixes/YYYYMMDD-HHMMSS
```

Rollback restores files only. The safe `gio` MIME association and
`bcp47langs` Wine registry override are intentionally left in place.

## What to expect during sign-in

A working Autodesk login flow should look roughly like this:

1. Fusion opens the Autodesk sign-in dialog.
2. The browser opens Autodesk Accounts.
3. After authentication, the browser calls `adskidmgr:/login?...`.
4. `fusion-callback-handler.sh` writes a callback request.
5. `fusion-browser-listener.sh` sends it to `AdskIdentityManager.exe`.
6. Fusion accepts the token and continues to the application UI.

Useful success indicators in the Neutron Platform log include:

```text
IDSDK immediatly returned success in sign-in dialog.
IDSDKAuth: idsdk_get_token returned IDSDK_E_SUCCESS
```

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for more detail.

## Notes about the Toolwindow Fixer

The patcher leaves:

```text
FUSION_ENABLE_TOOLWINDOW_FIXER=0
```

because the affected version can spawn many copies of
`fusion-toolwindow-fixer.exe`. Fusion remains usable without it. Some first-run
or tutorial overlays may have imperfect z-order under Wine; keyboard navigation
with `Tab`, `Space`, `Enter` or `Esc` can be used as a workaround.

## Documentation

- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Known issues](docs/KNOWN_ISSUES.md)
- [Tested configurations](docs/TESTED_CONFIGS.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Updating safely](docs/UPDATING.md)
- [Support policy](SUPPORT.md)
- [Security and privacy](SECURITY.md)
- [Roadmap](docs/ROADMAP.md)

## Contributing

Bug reports, working-setup reports, feature requests and pull requests are
welcome. GitHub issue forms collect the environment details needed to compare
Arch configurations without requiring users to paste sensitive login data.

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Supported scope

This project is intentionally narrow. It targets the currently observed Arch
issues around the `stonegray/fusion360-linux` launcher. It is not a complete
Fusion installer and does not attempt to support every desktop environment,
GPU driver or Proton build.

## Security / privacy

The patcher does not upload logs, Autodesk tokens, account IDs, browser data or
project files. Do **not** post full Autodesk callback URLs in public issues: they
may contain short-lived authentication codes and state values.

## Upstream

This project is meant as a small compatibility layer for:

- <https://github.com/stonegray/fusion360-linux>

If upstream incorporates a fix, the corresponding patch here can be retired.

## Releases

Pushing a version tag such as `v0.1.0` triggers the release workflow, which
creates ZIP and tar.gz source archives plus SHA-256 checksums.

See [docs/RELEASING.md](docs/RELEASING.md).

## License

The scripts and documentation in this repository are released under the MIT
License. Autodesk, Fusion and Fusion 360 are trademarks of Autodesk, Inc. This
project is unofficial and is not affiliated with or endorsed by Autodesk.
