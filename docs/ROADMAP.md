# Roadmap

The project follows observed compatibility problems rather than trying to become
a separate Fusion installer.

## Near term

- collect more working setup reports across NVIDIA, AMD and Intel GPUs;
- compare KDE Wayland, GNOME Wayland and X11 behavior;
- keep callback/login fixes compatible with upstream launcher changes;
- improve detection when upstream has already incorporated one of these fixes;
- expand unit tests for helper-script layout variants;
- document regressions by Proton version.

## Toolwindow Fixer

The current safe default is to keep the helper disabled. A future change may
re-enable it only after the process supervision logic can be proven not to
respawn duplicate helpers.

## Diagnostics

Keep diagnostics local-first and privacy-conscious. Future additions should
prefer allowlisted system information over dumping arbitrary logs.

## Upstreaming

Whenever a fix is generally useful and can be accepted upstream, prefer moving
it into `stonegray/fusion360-linux` and retiring the duplicate patch here.

## Packaging

If the project becomes stable across multiple reported systems, possible future
work includes an AUR helper package or a small wrapper package. This should wait
until the patch surface and upstream interaction are stable.
