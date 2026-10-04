# Tested configurations

This file separates **real-machine results** from what CI can validate.

## Real-machine working configuration

| Status | Distribution | Desktop | Session | GPU | Proton/Wine | Notes |
|---|---|---|---|---|---|---|
| Works with runtime fixes | CachyOS / Arch-based | KDE Plasma 6 | Wayland | NVIDIA GeForce RTX 3080 Ti | GE-Proton10-32 | Autodesk sign-in works after DLL-override/callback fixes. Toolwindow Fixer disabled; first-run overlay may require keyboard navigation. |

## Full-bootstrap status

The v0.2.0 bootstrap is tested in CI for:

- Python syntax and unit tests across multiple Python versions;
- source-transform idempotence and safety behavior;
- Bash syntax and ShellCheck;
- an Arch Linux container smoke test.

CI **cannot** complete Autodesk's proprietary GUI installer or real cloud
sign-in. Until a clean-machine working report is submitted, do not treat CI as
proof that every fresh Arch/CachyOS machine will complete the full Autodesk
installation unattended.

The default bootstrap pins upstream commit:

```text
c437488e1e73a19413295cb6ea74e357313bc359
```

At that revision upstream defaults to GE-Proton11-3. That is not the same
Proton version as the real-machine configuration above, so those results should
not be conflated.

## Add your configuration

Use the **Working setup report** issue form and include:

- distribution/version;
- kernel;
- desktop and Wayland/X11;
- GPU and driver;
- Proton/Wine version;
- `stonegray/fusion360-linux` revision;
- `fusion360-linux-arch-fixes` version;
- whether this was a fresh bootstrap or repair;
- output from `python3 fusion360_arch_fix.py check`;
- any remaining quirks.

Never include Autodesk callback URLs, login codes, tokens, email addresses or
private project data.
