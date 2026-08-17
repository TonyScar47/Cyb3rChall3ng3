# OS_1.01 — Missing people 1

---

## Problem description

First challenge in a 19-part OSINT series regarding a former missing person case. The goal is to identify Anthony's Instagram username profile URL using the archived case report provided in the challenge text.

## Recon

The challenge description links to an `archive.md` snapshot (`[https://archive.md/3yFWg](https://archive.md/3yFWg)`).
The attached `OSINT Challenges - README.pdf` specifies strict rules: purely passive OSINT, no interaction with targets or relatives, no active hacking, and respect for privacy.

## Solution, step by step

```bash
# 1. Open the archived page link in a browser:
#    https://archive.md/3yFWg

# 2. Scan the archived article/report for Anthony's full name, aliases, or direct social media links.

# 3. Construct the flag using the exact specified format:
#    https://www.instagram.com/<discovered_username>/
```

## Flag

```
****************
```

## What I learned

* Archived snapshots (`archive.md`) are critical OSINT assets for retrieving case details after pages or profiles go offline.
* Always check the exact flag format constraints (e.g., trailing slashes `/` and target case sensitivity) before submitting.