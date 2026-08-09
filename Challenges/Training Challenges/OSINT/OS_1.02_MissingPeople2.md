# OS_1.02 — Missing people 2

---

## Problem description

Second challenge in the OSINT series. The goal was to locate Anthony's secondary Instagram account—specifically the profile that contained zero posts.

## Recon

The challenge description notes that the original profile was taken down/removed from Instagram, rendering the live OSINT investigation impossible. As a result, the challenge is retained for archival purposes with the target handle disclosed directly by the authors.

## Solution, step by step

```bash
# 1. Read challenge description for target parameters (Anthony's empty IG profile).
# 2. Account no longer exists on live infrastructure.
# 3. Retrieve flag directly from the challenge archival statement:
#    https://www.instagram.com/buckeyeboi87/
```

> In live scenarios, discovering secondary empty profiles relies on username enumeration tools (like `sherlock` or `whatsmyname`), Google Dorking, or checking connected contacts/following lists on known accounts.

## Flag

```
CCIT{****************}
```

## What I learned

* OSINT target footprints are volatile: accounts can be removed, renamed, or set to private at any time.
* Always document and archive OSINT findings immediately using snapshots (e.g., `archive.org` / `archive.md`) before live targets disappear.