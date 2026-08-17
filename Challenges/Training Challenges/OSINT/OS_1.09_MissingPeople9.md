# OS_1.09 — Missing people 9

---

## Problem description

Ninth challenge in the OSINT "Missing people" series. The task is to establish **Anthony
Ginnetti's date of birth**, reported as month (in letters) and year (in numbers).

Flag format: `Month YYYY`

## Recon

Two independent lines converge on the answer, and the archived case report from OS_1.01
(`archive.md/3yFWg`) confirms it.

**Year — from age + handle signature.** Anthony's aunt Libby, in her November 13, 2021 appeal,
describes him as *"my 34 year old nephew,"* missing since **October 30, 2021**. That pins his birth
to the window **Nov 1986 – Oct 1987**. Every one of his personal handles carries the marker **87**
(`buckeyeboi87`, `tonyginnetti87`), which intersects the age window at exactly **1987**.

**Month — from a date-encoded handle.** Among his Instagram accounts is `anthonyginnetti0714`. The
`0714` is an `MMDD` birthday encoding → **07/14 = July 14**. July 14, 1987 is fully consistent with
him still being 34 on October 30, 2021.

## Exploit, step by step

```text
# 1. Fix the year from age + the "87" signature:
#      aunt's appeal: "34 year old", missing 30 Oct 2021  -> born Nov 1986 – Oct 1987
#      handles buckeyeboi87 / tonyginnetti87              -> 1987
#      intersection                                       -> 1987

# 2. Fix the month from the date-encoded handle:
#      instagram anthonyginnetti0714  ->  MMDD = 07/14  ->  July (14th)

# 3. Cross-check against the archived case report linked in OS_1.01 (archive.md/3yFWg),
#    which lists his date of birth: July 1987.
```

Both the handle evidence and the archived report agree: **July 1987**.

## Flag

```
****************
```

## What I learned

* **Numbers in usernames often encode a birthday.** `87` recurs as the birth year across his
  handles, and `anthonyginnetti0714` encodes the day as `MMDD` (July 14) — turning throwaway digits
  into a precise date.
* **Triangulate, don't rely on one source.** Age-at-disappearance narrows the year, the handle
  signature confirms it, and the archived report seals the exact month — three sources agreeing
  beats any single claim.
* **Archived reports are the ground truth.** The `archive.md` snapshot linked back in OS_1.01 held
  the case details all along; when live profiles hide a DOB, the preserved report is where to look.
* **Age math is a window, not a point.** "34 on 30 Oct 2021" alone allows late-1986 or 1987 — the
  extra signal (the "87" handles) is what collapses it to a single year.