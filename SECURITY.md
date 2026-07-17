# Security Policy

## Philosophy

“Increase Time, Increase Uncertainty.”

Security measures should be designed to make unauthorized access slow, noisy, and risky so the attacker’s best option is to give up. Because no single physical barrier is impervious to sustained force, the goal isn’t to guarantee defeat; it’s to raise the attacker’s time-to-compromise enough that deterrence and interruption take over. In practice, that means layered controls that delay, detect, and disrupt the attacker's efforts. I recognize that tools and dedication change the outcome so the system should be engineered so that, even when someone brings serious tools, they still lose time, get noticed, and can’t finish before intervention.

- Delay: Use layered physical barriers (secure placement, tamper-resistant mounting, hardening weak points) so cutting/prying takes longer.
- Detect: Ensure attempts trigger consequences quickly (keyfile integrity verification, cryptographic handshakes).
- Disrupt: Pair detection with escalation (system panic, lockout/wipeout, procedures that make it hard to “keep working” unnoticed).
- Disincentivize: Secure the access path (location, enclosures, tamper-resistance) so the bottleneck isn’t only the operating objective.

## Supported Versions

The following versions of AutoSecurityBox are being routinely updated.

| Version | Supported          |
| ------- | ------------------ |
| 1.9.x   | :white_check_mark: |
| 1.8.x   | :white_check_mark: |

## Reporting a Vulnerability or Suggestion

To report a security vulnerability or suggestion, Use the "Report A Vulnerability" button on the "Advisories" page.
