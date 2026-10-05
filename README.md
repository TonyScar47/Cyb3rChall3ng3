# 🏆 Cyb3rChall3ng3 — CyberChallenge.IT Writeups

Writeups and notes from the challenges I worked through during the **CyberChallenge.IT** training program, CINI's cybersecurity training initiative. They cover Web, Network, Access Control, Hardware and OSINT.

This repo contains **only the challenges I actually solved**, not the full set offered by the platform: some categories or numbers may be missing, and that's expected.

## How it's organized

Two tiers:

- **Introduction** — compact walkthroughs of the platform-guided introductory challenges, one page per category.
- **Training Challenges** — the real, reasoned writeups: one challenge per file, grouped by category.

## Conventions

- **Flags are redacted** (`CCIT{****************}`): you'll find the method and the exploit here, not a ready-to-paste answer.
- Every training writeup follows the same structure: *Problem description → Recon/Analysis → Exploit step by step → Flag → What I learned*.
- File numbering mirrors the platform's, so it **may have gaps**: those are the challenges I didn't solve (or didn't document).

## Index

### 📘 Introduction
- [Web Security](Challenges/Introduction/Web_Security.md)
- [Network Security](Challenges/Introduction/Network_Security.md)
- [Software Security](Challenges/Introduction/Software_Security.md)
- [Cryptography](Challenges/Introduction/Cryptography.md)

### 🧪 Training Challenges

- **Web Security** — [WebSecurity1](Challenges/Training%20Challenges/WebSecurity1) (RCE, LFI, SSRF, upload), [WebSecurity2](Challenges/Training%20Challenges/WebSecurity2) (SQL/NoSQL injection), [WebSecurity3](Challenges/Training%20Challenges/WebSecurity3) (XSS)
- **Network Security** — [NetworkSecurity0](Challenges/Training%20Challenges/NetworkSecurity0) (fundamentals: ports, handshake, routing, NAT), [NetworkSecurity1](Challenges/Training%20Challenges/NetworkSecurity1), [NetworkSecurity2](Challenges/Training%20Challenges/NetworkSecurity2)
- **Access Control** — [Access Control](Challenges/Training%20Challenges/Access%20Control) (privilege escalation: SUID, PATH hijacking, ...)
- **Hardware Security** — [HardwareSecurity1](Challenges/Training%20Challenges/HardwareSecurity1) (DSP and instruction reversing)
- **OSINT** — [OSINT](Challenges/Training%20Challenges/OSINT) (Missing People and Domain recon, purely passive)

## 🧰 Resources

Supporting tools and material (not writeups):

- [`attack-defense-cheatsheet.md`](resources/attack-defense-cheatsheet.md) — playbook for the opening minutes of an Attack/Defense game
- [`cli-reference.md`](resources/cli-reference.md) — Linux / pwn / security command reference
- [`setup.sh`](resources/setup.sh) — CTF environment provisioning on Arch Linux

---

*Writeups by **TonyScar47** — CyberChallenge.IT 2026 (CINI) · National Finalist @ PoliBa · Bari, Apulia (Italy).*