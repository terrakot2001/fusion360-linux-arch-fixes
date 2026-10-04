# Security and privacy

This project modifies launcher/helper files around an existing
`stonegray/fusion360-linux` installation. It does not distribute Autodesk
software and should never need Autodesk credentials.

## Never post these publicly

Do not include any of the following in an issue, pull request, screenshot or
diagnostic attachment:

- full `adsk://` or `adskidmgr://` callback URLs;
- OAuth/login `code`, `state`, access tokens or ID tokens;
- Autodesk account IDs or email addresses;
- browser cookies or session data;
- private Fusion project files or customer data.

If you accidentally publish a live authentication value, delete/redact the
content and re-authenticate with Autodesk. Treat the exposed value as sensitive.

## Reporting a security problem

If the problem can be described without a secret, open an issue with the
minimum technical detail necessary and clearly mark it as a security concern.

If disclosure would require posting credentials, tokens or private data, do
**not** open a public issue containing that data. Use GitHub's private security
reporting feature if it is available for this repository, or open a minimal
public issue asking the maintainer for a private contact channel without
including the sensitive details.

## Diagnostic policy

The project-provided diagnostic script writes a local text file only. It does
not upload anything. Review every diagnostic file before attaching it to an
issue.
