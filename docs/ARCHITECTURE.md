# Architecture

The project has two layers:

1. a **fresh-install bootstrap** around `stonegray/fusion360-linux`;
2. an **idempotent runtime patcher** for existing installations.

It does not fork or redistribute Autodesk Fusion.

## Fresh-install flow

```text
install.sh
   |
   +-- existing install? ---- yes ---> fusion360_arch_fix.py apply/check
   |
   no
   v
fusion360_bootstrap.py
   |
   +--> verify Arch-family host / desktop / sudo
   +--> clone pinned stonegray/fusion360-linux
   +--> patch upstream source before installation
   |      +--> Arch package list
   |      +--> WINEDLLOVERRIDES
   |      +--> prefix-scoped process shutdown
   |      +--> Toolwindow Fixer safeguards
   |      +--> callback/browser log redaction
   |      +--> safe upstream --kill
   |
   +--> run upstream full installer
   |      +--> system dependencies
   |      +--> GE-Proton
   |      +--> Proton prefix / winetricks
   |      +--> WebView2/runtime setup
   |      +--> official Autodesk Fusion downloader
   |      +--> desktop/file associations
   |
   +--> patch installed runtime again
   +--> bcp47langs Wine registry override
   +--> gio callback associations
   +--> syntax + configuration checks
   +--> verify Fusion360.exe
   +--> install maintenance commands + provenance
   v
ready local installation
```

## Existing-install flow

```text
fusion360_arch_fix.py apply
        |
        +--> timestamped backup
        +--> config compatibility values
        +--> launcher WINEDLLOVERRIDES fix
        +--> prefix-scoped cleanup/process management
        +--> Toolwindow Fixer safeguards
        +--> callback/browser log redaction
        +--> Autodesk callback registration via gio
        +--> bcp47langs Wine registry override
        +--> Bash syntax validation
        v
patched local installation
```

## Design goals

### Reproducible bootstrap

The default full installer uses a pinned upstream commit. Users can opt into
upstream `dev`, but the pin is safer because source transforms target a known
file layout.

### Idempotent runtime repair

Running the runtime patcher repeatedly should not duplicate configuration lines
or shell fragments.

### Minimal Autodesk surface

Autodesk application files under `webdeploy` are not patched. The project
changes Linux-side launcher/helper scripts, the Fusion Wine prefix configuration
and desktop protocol associations.

### Reversible file changes

Before each runtime apply, files that may be changed are copied into a
timestamped backup with a manifest.

### Prefix isolation

Shutdown logic targets only the configured Fusion Wine prefix. Generic matching
of all user-owned `wine`, `proton`, `node.exe` or `steam-runtime` processes is
deliberately avoided.

### Authentication privacy

The callback itself must contain a real short-lived authentication URL to work,
but helper logs do not need to store it. The privacy patch preserves the
transient request flow while redacting raw browser/callback URLs and arguments.

## Intentionally untouched

- Autodesk Fusion application payloads under `webdeploy`;
- Autodesk account/licensing state;
- global Wine configuration outside the Fusion prefix;
- unrelated Steam/Proton/Wine prefixes;
- third-party Vulkan layers.
