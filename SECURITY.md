# Security Policy

## Reporting a vulnerability

Please report security problems **privately**, not in public issues: use GitHub's private vulnerability
reporting on this repository (*Security* tab, *Report a vulnerability*).

Include the version (`mindas-terminal --version`), your operating system, shell and host terminal, and the
steps to reproduce. You will get an acknowledgement within 7 days. Reporters are credited in the changelog
unless they prefer otherwise.

## Supported versions

| Version | Supported |
|---|---|
| 0.1.x | Yes |
| < 0.1 | No |

## Scope

In scope: anything that lets output, pasted text, settings files or toolkit values cause actions the user did
not intend, leaks data, or crashes or freezes the terminal.

The threat model and every protection, with the tests that check it, are documented in
[docs/Security.md](docs/Security.md).

## Ethical use

This project serves defenders, engineers, researchers, students and authorised testers. Use the security
toolkit only on systems you own or are authorised in writing to test. Contributions intended for
unauthorised access, detection evasion, or harm are not accepted.
