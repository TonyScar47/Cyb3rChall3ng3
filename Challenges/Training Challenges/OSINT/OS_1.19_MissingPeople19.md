# OS_1.19 — Missing people 19

---

## Problem description

Nineteenth challenge in the "Missing people" series. It asks to determine the exact date of death of Anthony's mother (`Theresa Ginnetti`), identified in the previous challenge.

Flag format: `YYYY/MM/DD`.

## Recon

With Anthony's mother identified as **Theresa Ginnetti** in the preceding challenge, the fastest route to find vital event dates is searching for indexed obituary records published by local funeral homes or memorial aggregators.

## Solution, step by step

1. Search Google for **`"Theresa Ginnetti"`**.
2. Click the top search result leading to the memorial obituary page: `[https://www.maederquinttiberi.com/obituary/4646702](https://www.maederquinttiberi.com/obituary/4646702)`.
3. Locate the recorded date of death on the obituary notice (**December 11, 2007**).
4. Format the extracted date according to the required `YYYY/MM/DD` syntax (`2007/12/11`).

## Flag

```text
****************
```

## What I learned

* **Funeral Home Indexing:** Memorial entries on funeral home domains (such as `maederquinttiberi.com`) rank very highly on search engines for exact-name queries and provide direct, unredacted vital dates.
* **Format Conversion:** Vital dates in public obituaries are typically written in natural language (e.g., *Month DD, YYYY*) and must be converted to the standardized `YYYY/MM/DD` format for flag submission.