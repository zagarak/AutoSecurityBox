# Security Policy

## Philosophy

“Increase Time, Increase Uncertainty.”

Security measures should be designed to make unauthorized access slow, noisy, and risky so the attacker’s best option is to give up. Because no single physical barrier is impervious to sustained force, the goal isn’t to guarantee defeat; it’s to raise the attacker’s time-to-compromise enough that deterrence and interruption take over and the attacker moves on to an easier target.

- Delay: Use layered physical barriers (secure placement, tamper-resistant mounting, hardening weak points) so cutting/prying takes longer.
- Detect: Ensure attempts trigger consequences quickly (key file integrity verification, eventually cryptographic handshakes).
- Disrupt: Pair detection with escalation (system panic, lockout/wipeout, procedures that make it hard to “keep working” unnoticed).
- Disincentivize: Secure the access path (location, enclosures, software tamper-resistance) so the bottleneck isn’t solely physical barriers.

## Supported Versions

The following versions of AutoSecurityBox are being routinely updated.

| Version | Supported          |
| ------- | ------------------ |
| 1.9.x   | :warning:          |
| 1.8.x   | :white_check_mark: |

## Reporting a Vulnerability or Suggestion

To report a security vulnerability or suggestion, Use the "Report A Vulnerability" button on the "Advisories" page.
