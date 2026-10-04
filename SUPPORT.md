# Support policy

This repository is an **unofficial compatibility project**. It is not Autodesk
support and is not affiliated with Autodesk.

## In scope

Issues are in scope when they involve the Arch/Arch-based compatibility layer
around `stonegray/fusion360-linux`, especially:

- installer dependency naming on Arch;
- Wine/Proton environment and DLL override handling;
- Autodesk browser callback registration;
- Identity Manager startup/login regressions caused by the launcher environment;
- helper process runaway/restart behavior;
- cleanup that affects unrelated Wine/Proton prefixes;
- Arch/CachyOS-specific launcher integration.

## Usually out of scope

These are usually better reported elsewhere unless the compatibility layer is
clearly involved:

- Fusion design/modeling bugs that also occur on Windows/macOS;
- Autodesk licensing/account policy questions;
- Autodesk cloud outages;
- general GPU hardware failures;
- unrelated Steam/Proton game issues;
- unsupported third-party Vulkan layers;
- problems in upstream `stonegray/fusion360-linux` that reproduce unchanged on
  non-Arch distributions.

## Before asking for help

Run:

```bash
python3 fusion360_arch_fix.py check
bash scripts/collect-diagnostics.sh
```

Then use the most appropriate GitHub issue form.

Always review diagnostic output before posting it.
