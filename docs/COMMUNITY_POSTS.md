# Community announcement pack

Ready-to-post descriptions for sharing **Fusion 360 Linux Arch Fixes** with
different communities. Keep the tone technical and transparent: this is an
unofficial compatibility project, not Autodesk support, and fresh-install
testing on more real machines is still welcome.

Project:
https://github.com/terrakot2001/fusion360-linux-arch-fixes

## CachyOS Forum

### Suggested title

**Fusion 360 on CachyOS/Arch — full installer + login/runtime fixes**

### Post

I put together an unofficial Arch/CachyOS companion project for
`stonegray/fusion360-linux` after working through several issues around
installation, Autodesk sign-in and Wine/Proton cleanup.

The project now supports both:

- a fresh installation from scratch;
- repair/update of an existing `stonegray/fusion360-linux` setup.

On a fresh system:

```bash
git clone https://github.com/terrakot2001/fusion360-linux-arch-fixes.git
cd fusion360-linux-arch-fixes
bash install.sh
```

The installer detects Arch-family systems, clones a pinned upstream revision,
applies the Arch fixes before installation, runs the upstream Fusion/Proton
setup, applies the runtime fixes again, and verifies the result.

Current fixes include:

- Arch dependency fix: `python3-tk` -> `tk`;
- corrected Wine DLL override handling;
- Autodesk Identity Manager / `bcp47langs` workaround;
- Autodesk browser callback registration through `gio`;
- protection against runaway Toolwindow Fixer processes;
- Fusion-prefix-scoped Wine shutdown so unrelated Proton/Wine apps are not
  killed;
- private per-user authentication bridge files and redacted callback logs;
- backup/restore and verification commands.

CI currently covers Python 3.10-3.13, ShellCheck, an Arch Linux smoke test, and
a real source-patch test against the pinned `stonegray/fusion360-linux`
revision.

The runtime/login fixes have worked on a real CachyOS + KDE Plasma 6 + Wayland +
NVIDIA setup. The part I would especially like more community feedback on now is
the **full clean-machine install path** across more GPUs and desktops.

Repo:
https://github.com/terrakot2001/fusion360-linux-arch-fixes

Fresh-install tracking:
https://github.com/terrakot2001/fusion360-linux-arch-fixes/issues/3

This is unofficial and not affiliated with Autodesk.

---

## Reddit — r/Fusion360

### Suggested title

**I made a one-command-ish Fusion 360 installer/repair layer for Arch/CachyOS**

### Post

I have been testing Fusion 360 on CachyOS/Arch through Proton and ended up
turning the fixes into a public project:

https://github.com/terrakot2001/fusion360-linux-arch-fixes

The goal is not to redistribute Fusion. It wraps
`stonegray/fusion360-linux`, applies the Arch-specific fixes before install,
then verifies/repairs the installed runtime.

Fresh install:

```bash
git clone https://github.com/terrakot2001/fusion360-linux-arch-fixes.git
cd fusion360-linux-arch-fixes
bash install.sh
```

The same `install.sh` also detects an existing installation and switches to
repair/update mode.

Some of the problems it handles:

- Arch's `python3-tk` package mismatch;
- Autodesk login / Identity Manager issues;
- browser callback handling;
- malformed Wine DLL overrides;
- runaway helper processes;
- cleanup that could otherwise affect unrelated Proton/Wine applications.

It also adds backups, diagnostics and CI tests against a pinned upstream
revision.

What I still need most is **fresh-install feedback from other machines**,
especially AMD/Intel GPUs, GNOME and X11.

If anyone tests it, please report the environment here:
https://github.com/terrakot2001/fusion360-linux-arch-fixes/issues/3

Unofficial project, not supported by Autodesk.

---

## Reddit — r/linux

### Suggested title

**Open-source Arch/CachyOS bootstrap for running Fusion 360 through Proton**

### Post

I have published an Arch-family bootstrap/repair layer around
`stonegray/fusion360-linux`:

https://github.com/terrakot2001/fusion360-linux-arch-fixes

It is intentionally not a Fusion redistribution. It automates the Linux-side
setup and compatibility work:

- patches Arch dependencies before upstream install;
- installs through the upstream Proton-based workflow;
- applies Autodesk sign-in/browser callback fixes;
- scopes Wine cleanup to the Fusion prefix;
- protects transient authentication bridge data;
- verifies the final runtime and provides repair/diagnostic commands.

The same entry point handles fresh installs and existing installs:

```bash
git clone https://github.com/terrakot2001/fusion360-linux-arch-fixes.git
cd fusion360-linux-arch-fixes
bash install.sh
```

The project has CI for Python 3.10-3.13, ShellCheck, Arch Linux, and a pinned
upstream source-patching smoke test.

Real-machine runtime/login testing has been done on CachyOS + KDE Plasma 6 +
Wayland + NVIDIA. I am looking for more clean-install reports from other Arch
setups, especially AMD/Intel and GNOME.

This is an unofficial community workaround and is not affiliated with Autodesk.

---

## Arch Linux Forums

### Suggested title

**Fusion 360 via Proton — Arch-specific bootstrap and compatibility fixes**

### Post

For anyone experimenting with Fusion 360 on Arch via Proton, I have published a
small compatibility/bootstrap project around `stonegray/fusion360-linux`:

https://github.com/terrakot2001/fusion360-linux-arch-fixes

It primarily addresses Arch-specific and launcher/runtime issues rather than
Fusion itself.

Notable changes:

- fixes `python3-tk` -> `tk` in the Arch dependency list;
- uses `glib2/gio` for Autodesk callback registration;
- fixes independent `WINEDLLOVERRIDES` separators;
- persists the `bcp47langs` Wine override used by Autodesk Identity Manager;
- scopes shutdown to the configured Fusion Wine prefix;
- disables/guards the affected Toolwindow Fixer path;
- moves authentication bridge files to a private per-user runtime directory;
- redacts callback URLs from helper logs;
- backs up modified runtime files and supports restore.

For fresh Arch installations:

```bash
git clone https://github.com/terrakot2001/fusion360-linux-arch-fixes.git
cd fusion360-linux-arch-fixes
bash install.sh
```

The default bootstrap pins a known upstream commit so text/source transforms are
reproducible rather than silently following layout changes in `dev`.

CI includes an Arch container smoke test and also clones the pinned upstream,
applies the full patch set twice, and verifies idempotence.

Reports from additional Arch configurations are welcome:
https://github.com/terrakot2001/fusion360-linux-arch-fixes/issues/3

---

## Autodesk Community

### Suggested title

**Unofficial Linux community installer/compatibility layer for Fusion 360 on Arch**

### Post

For Linux users who are already experimenting with Fusion 360 through
Wine/Proton, I have published an unofficial community project for Arch-based
distributions:

https://github.com/terrakot2001/fusion360-linux-arch-fixes

This is **not an Autodesk-supported build** and it does not redistribute Fusion.
It uses the official Fusion downloader through the existing community
`stonegray/fusion360-linux` workflow and automates a number of Linux-specific
installation, login and cleanup fixes.

The current project provides:

- fresh install and repair/update modes;
- Arch/CachyOS dependency fixes;
- Autodesk browser callback / Identity Manager workarounds;
- safer Wine/Proton cleanup;
- backup and diagnostics;
- automated CI against Arch and a pinned upstream source revision.

I am sharing it mainly so Linux users who already rely on unofficial Proton
workarounds can test the same reproducible setup and report compatibility
results.

Project:
https://github.com/terrakot2001/fusion360-linux-arch-fixes

Fresh-install test matrix:
https://github.com/terrakot2001/fusion360-linux-arch-fixes/issues/3

Again, this is a community workaround and is not affiliated with or endorsed by
Autodesk.

---

## stonegray/fusion360-linux — issue/PR comment

I have been testing the Arch/CachyOS path and built a companion compatibility
layer around this project:

https://github.com/terrakot2001/fusion360-linux-arch-fixes

The intent is to keep Arch-specific fixes isolated and eventually retire them
whenever equivalent fixes land upstream.

The companion project currently covers:

- `python3-tk` -> `tk` for Arch;
- `glib2/gio` callback registration;
- DLL-override fixes used by Autodesk Identity Manager;
- prefix-scoped Wine shutdown;
- Toolwindow Fixer runaway-process safeguards;
- private/redacted Autodesk callback bridge handling;
- backup/restore and CI against a pinned upstream revision.

It can perform a full fresh install or repair an existing installation.

I would be happy to upstream generally useful pieces rather than maintain
duplicate behavior permanently.
