## What does this change?

Describe the problem and the fix.

## Scope

- [ ] The change is limited to the Arch/Arch-based Fusion compatibility layer.
- [ ] It does not redistribute Autodesk software or proprietary binaries.
- [ ] It does not collect or upload user data, logs, tokens or project files.

## Testing

- [ ] `python -m py_compile fusion360_arch_fix.py`
- [ ] `python -m unittest discover -s tests -v`
- [ ] `bash -n install.sh check.sh scripts/*.sh`
- [ ] I tested the change on a real or representative `fusion360-linux` tree, when applicable.
- [ ] Re-running the patch is safe/idempotent.

## Environment tested

Distribution:
Desktop / Wayland or X11:
GPU / driver:
Proton / Wine:
`stonegray/fusion360-linux` commit/tag:

## Privacy check

- [ ] No Autodesk callback codes, access tokens, account IDs, email addresses or private project data are included.
