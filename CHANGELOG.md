# Changelog

## 0.2.0 - 2026-10-04

Full-install release.

- Smart `install.sh`: fresh install or existing-install repair automatically.
- Added `fusion360_bootstrap.py`, `install-fresh.sh`, `repair.sh`, and `quick-install.sh`.
- Pinned upstream revision by default, with opt-in `--latest-upstream` mode.
- Applies Arch/runtime safety patches before the upstream installer runs.
- Added `glib2` for reliable `gio` callback registration on Arch.
- Replaced broad Wine/Proton shutdown with Fusion-prefix-scoped shutdown.
- Redacts raw Autodesk authentication URLs/arguments from helper logs.
- Verifies the final Fusion payload and installs persistent maintenance commands.
- Added installation provenance metadata and full-install documentation.
- Expanded tests for source transforms, bootstrap logic, Bash, ShellCheck, and Arch.


## 0.1.0 - 2026-10-04

Initial public version.

- Arch `python3-tk` -> `tk` compatibility fix.
- Correct semicolon separation in `WINEDLLOVERRIDES`.
- Persistent `bcp47langs` override for Autodesk Identity Manager.
- Toolwindow Fixer runaway-process safeguards.
- Prefix-scoped Fusion cleanup.
- Autodesk callback registration through `gio`.
- Backup, verify and restore commands.
- Arch/CachyOS troubleshooting documentation.
- Privacy-conscious local diagnostics collector.
- Bug, support, feature-request and working-setup issue forms.
- Pull-request template, support/security policies and tested-config matrix.
- Ubuntu/Python matrix, ShellCheck and Arch Linux CI smoke tests.
- Automated source release workflow for version tags.
