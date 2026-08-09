# OS_1.03 — Missing people 3

---

## Problem description

Third challenge in the OSINT series. The objective is to discover Anthony's primary Facebook account URL, specifically selecting the profile with the higher friend count if multiple accounts exist.

## Recon

Using the target's full name (*Anthony Michael Ginnetti*) and previously discovered handles (`whtboi2real100` / `buckeyeboi87`), we search Facebook to identify matching candidate profiles.

## Solution, step by step

```bash
# 1. Search Facebook / Google Dorking for target profiles:
#    site:facebook.com "Anthony Ginnetti"

# 2. Inspect candidate profiles to compare public friend counts.

# 3. Extract the username/slug from the URL of the primary account:
#    https://www.facebook.com/<discovered_username>
```

> Pay close attention to the flag format in this challenge: unlike previous tasks, the description example (`[https://www.facebook.com/USERNAME](https://www.facebook.com/USERNAME)`) omits a trailing slash.

## Flag

```
CCIT{****************}
```

## What I learned

* Targets often maintain multiple accounts on the same platform (e.g., old/abandoned vs active profiles).
* Friend counts and public interactions serve as reliable indicators to distinguish an active main account from alt/burn accounts.