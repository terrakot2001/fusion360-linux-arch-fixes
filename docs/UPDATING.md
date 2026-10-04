# Updating safely

There are two moving parts:

1. this compatibility repository;
2. the upstream `stonegray/fusion360-linux` installation.

## Update this project

```bash
cd fusion360-linux-arch-fixes
git pull --ff-only
python3 fusion360_arch_fix.py --version
```

## After updating stonegray/fusion360-linux

Upstream updates can replace files that this project patched.

Run:

```bash
python3 fusion360_arch_fix.py check
```

If checks fail, re-apply:

```bash
bash install.sh
```

A fresh timestamped backup is created before changes.

## If a new upstream version changes the script layout

Do not force-edit the file blindly. Open a bug report and include:

- the upstream commit/tag;
- the failed `check` output;
- the exact patcher error;
- a sanitized snippet of the affected helper script.

## Restore

List backups:

```bash
python3 fusion360_arch_fix.py backups
```

Restore the latest file backup:

```bash
python3 fusion360_arch_fix.py restore
```

The restore command intentionally restores files only. MIME associations and the
Wine registry override are not automatically removed.
