# Architecture

The project is deliberately small. It patches an existing
`stonegray/fusion360-linux` installation rather than replacing the upstream
launcher.

## Flow

```text
existing fusion360-linux
        |
        v
fusion360_arch_fix.py
        |
        +--> timestamped backup
        |
        +--> config compatibility values
        |
        +--> launcher WINEDLLOVERRIDES fix
        |
        +--> prefix-scoped Wine cleanup
        |
        +--> Toolwindow Fixer safeguards
        |
        +--> Autodesk callback registration via gio
        |
        +--> bcp47langs Wine registry override
        |
        +--> bash syntax validation
        v
patched local installation
```

## Design goals

### Idempotent

Running the patcher repeatedly should not duplicate configuration lines or add
repeated shell fragments.

### Minimal

Only known compatibility problems are changed. Autodesk application files are
not modified.

### Reversible files

Before each apply, files that may be changed are copied into a timestamped
backup directory with a manifest.

### Prefix isolation

Shutdown logic is scoped to the configured Fusion Wine prefix. The project
avoids generic process matching such as every `wine`, `proton`, `node.exe`
or `steam-runtime` process owned by the user.

### Explicit login bridge

Autodesk browser callbacks are associated with the desktop callback handler via
`gio mime`. The Wine registry also carries the `bcp47langs` override so
Autodesk Identity Manager does not depend only on inherited launcher
environment variables.

## What is intentionally not patched

- Autodesk binaries;
- Fusion application payloads under `webdeploy`;
- third-party Vulkan layers;
- global Wine configuration outside the Fusion prefix;
- unrelated Steam/Proton prefixes.
