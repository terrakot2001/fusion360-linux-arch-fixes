# Tested configurations

This table contains configurations that have been directly tested or reported
through this project. A single successful row is **not** a guarantee for every
system.

| Status | Distribution | Desktop | Session | GPU | Proton/Wine | Notes |
|---|---|---|---|---|---|---|
| Works with fixes | CachyOS / Arch-based | KDE Plasma 6 | Wayland | NVIDIA GeForce RTX 3080 Ti | GE-Proton10-32 | Autodesk sign-in works after DLL-override/callback fixes. Toolwindow Fixer left disabled; first-run overlay may require keyboard navigation. |

## Add your configuration

Use the **Working setup report** issue form. Useful details are:

- distribution/version;
- kernel;
- desktop and Wayland/X11;
- GPU and driver;
- Proton/Wine version;
- `stonegray/fusion360-linux` revision;
- output from `python3 fusion360_arch_fix.py check`;
- any remaining quirks.

Never include Autodesk callback URLs, login codes, tokens, email addresses or
private project data.
