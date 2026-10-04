# Full installation

The project can now perform a complete first-time Fusion 360 setup on
Arch-family distributions.

## Recommended install

Clone the repository so you can inspect exactly what will run:

```bash
git clone https://github.com/terrakot2001/fusion360-linux-arch-fixes.git
cd fusion360-linux-arch-fixes
bash install.sh
```

`install.sh` is smart:

- if Fusion is not installed, it performs the full bootstrap;
- if Fusion is already installed, it applies/verifies the compatibility fixes.

For an explicitly fresh-only run:

```bash
bash install-fresh.sh
```

For repair only:

```bash
bash repair.sh
```

## What a fresh install does

1. Confirms the host is Arch/CachyOS/another Arch-family distribution.
2. Checks that it is running as a normal desktop user, not root.
3. Ensures bootstrap dependencies are available.
4. Clones a pinned `stonegray/fusion360-linux` revision into a temporary cache.
5. Applies the Arch fixes **before upstream installation begins**, including:
   - `python3-tk` -> `tk`;
   - adding Arch's `glib2` for `gio`;
   - corrected `WINEDLLOVERRIDES` separators;
   - prefix-scoped Wine/Proton shutdown;
   - Toolwindow Fixer runaway safeguards;
   - redaction of authentication URLs/arguments from helper logs;
   - safe upstream `--kill` behavior.
6. Runs upstream's full installer, which installs system dependencies, GE-Proton,
   the Proton prefix, WebView2/runtime prerequisites, and downloads the official
   Fusion Client Downloader from Autodesk's CDN.
7. Applies the runtime patch set again to the installed copy.
8. Adds the persistent `bcp47langs` Wine registry override.
9. Registers `adsk://` and `adskidmgr://` with `gio`.
10. Verifies shell syntax, configuration, callback handlers and the Fusion payload.
11. Installs maintenance commands in `~/.local/bin`.

The project does **not** redistribute Fusion 360 or Autodesk binaries.

## Reproducibility

The default full installer pins upstream to:

```text
c437488e1e73a19413295cb6ea74e357313bc359
```

This is intentional: source patches are safer when applied to a known source
layout.

To try current upstream `dev` instead:

```bash
bash install-fresh.sh --latest-upstream
```

That mode is less reproducible and may require patch updates if upstream has
changed.

## Optional flags

```text
--launch             Launch Fusion after installation.
--keep-source        Keep the patched upstream source after a successful install.
--prepare-only       Clone + patch upstream, but do not install anything.
--upstream-ref REF   Use a specific upstream branch/tag/commit.
--latest-upstream    Use upstream dev instead of the pinned revision.
--work-base DIR      Choose where temporary source is prepared.
```

## Maintenance commands after installation

```bash
fusion360-arch-check
fusion360-arch-repair
fusion360-arch-diagnostics
fusion360-safe-stop
```

`fusion360-safe-stop` terminates only the Fusion Wine prefix; it is not intended
to kill unrelated games or Wine applications.

## Convenience one-liner

For users who understand the risks of executing a remote script directly:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/terrakot2001/fusion360-linux-arch-fixes/main/quick-install.sh)
```

The clone-and-review method above is preferred.

## Existing installation

The full bootstrap deliberately refuses to overwrite an existing setup.
Use:

```bash
bash install.sh
```

or:

```bash
bash repair.sh
```

to update the patch set on an existing installation.

## End-to-end testing note

CI can test the patch transforms and Arch shell/Python behavior, but it cannot
fully exercise Autodesk's proprietary GUI installer or interactive cloud sign-in
inside GitHub Actions. Real-machine working reports are therefore important.
Use the repository's **Working setup report** issue form to add a configuration.
