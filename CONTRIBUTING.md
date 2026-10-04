# Contributing

Bug reports and small compatibility patches are welcome.

Please include:

- distribution and version;
- desktop environment and display protocol (X11/Wayland);
- Proton/Wine build;
- the output of `python3 fusion360_arch_fix.py check`;
- only sanitized log excerpts.

Do not post Autodesk authentication callback URLs, access tokens, account IDs or
private project data.

Keep patches narrowly scoped and idempotent. Prefer modifying only
`fusion360-linux` helper scripts and configuration rather than Autodesk files.
