# Support policy

This repository is an **unofficial compatibility project**. It is not Autodesk
support and is not affiliated with Autodesk.

## In scope

Issues are in scope when they involve the Arch-family bootstrap or compatibility
layer around `stonegray/fusion360-linux`, especially:

- fresh installation through `fusion360_bootstrap.py` / `install-fresh.sh`;
- installer dependency naming on Arch;
- pinned-upstream source patch failures;
- Wine/Proton environment and DLL override handling;
- Autodesk browser callback registration;
- Identity Manager startup/login regressions caused by launcher environment;
- helper process runaway/restart behavior;
- cleanup that affects unrelated Wine/Proton prefixes;
- Arch/CachyOS desktop integration;
- post-install verification or maintenance commands.

## Usually out of scope

- Fusion design/modeling bugs that also occur on Windows/macOS;
- Autodesk licensing/account policy questions;
- Autodesk cloud outages;
- general GPU hardware failures;
- unrelated Steam/Proton game issues;
- unsupported third-party Vulkan layers;
- upstream issues that reproduce unchanged on non-Arch distributions.

## Before asking for help

From a repository clone:

```bash
python3 fusion360_arch_fix.py check
bash scripts/collect-diagnostics.sh
```

After a successful full install:

```bash
fusion360-arch-check
fusion360-arch-diagnostics
```

Then use the most appropriate GitHub issue form.

Always review diagnostic output before posting it. Never publish Autodesk
callback URLs, login codes, tokens, account IDs or private project data.
