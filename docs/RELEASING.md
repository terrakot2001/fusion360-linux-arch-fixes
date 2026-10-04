# Releasing

The repository contains a GitHub Actions workflow that creates source archives
and SHA-256 checksums whenever a version tag matching `v*` is pushed.

## Before tagging

Run locally:

```bash
bash scripts/selftest.sh
```

Update:

- `VERSION` in `fusion360_arch_fix.py`;
- `CHANGELOG.md`;
- README notes if behavior changed.

Commit those changes first.

## Create a release tag

Example:

```bash
git tag -a v0.1.0 -m "Fusion 360 Linux Arch Fixes v0.1.0"
git push origin v0.1.0
```

GitHub Actions will create a Release containing:

- `fusion360-linux-arch-fixes-vX.Y.Z.tar.gz`;
- `fusion360-linux-arch-fixes-vX.Y.Z.zip`;
- `SHA256SUMS.txt`.

GitHub-generated source archives will also remain available.

## If the workflow fails

Do not reuse or move a published release tag silently. Fix the workflow, decide
whether the failed tag was externally consumed, and use a new patch version
when appropriate.
