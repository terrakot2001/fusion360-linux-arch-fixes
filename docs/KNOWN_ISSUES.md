# Known issues and limitations

## Toolwindow Fixer remains disabled

The observed helper implementation can create repeated
`fusion-toolwindow-fixer.exe` processes. The patcher therefore keeps:

```text
FUSION_ENABLE_TOOLWINDOW_FIXER=0
```

This avoids the runaway process problem. The tradeoff is that a first-run or
tutorial overlay can occasionally have imperfect z-order under Wine/KDE.

## First-run overlay cannot be clicked

Try keyboard navigation:

- `Tab` — move focus;
- `Space` — toggle;
- `Enter` — activate;
- `Esc` — dismiss when supported.

After onboarding is completed this normally stops being relevant.

## xdg-mime may fail on some KDE/Arch setups

Some systems have an `xdg-mime` path that expects `qtpaths` or older KDE
helpers. The project uses `gio mime` for Autodesk callback registration instead
of relying on that path.

## Unrelated Vulkan implicit-layer warnings

A warning from another implicit Vulkan layer, for example a missing symbol in a
third-party layer library, is not automatically a Fusion problem. This project
does not remove third-party Vulkan layers.

## Upstream changes can invalidate a text patch

`stonegray/fusion360-linux` may change its helper scripts. The patcher refuses
some transformations when the expected section cannot be found instead of
blindly injecting code. Run `python3 fusion360_arch_fix.py check` after upstream
updates and report new layouts with the upstream revision.

## Personal Use / trial licensing

This project only affects Linux compatibility. Autodesk subscription, trial and
Personal Use entitlement behavior is controlled by Autodesk and is outside the
scope of this repository.
