# OS_1.06 — Missing people 6

---

## Problem description

Sixth challenge in the OSINT "Missing people" series. The objective is to identify **Anthony's
relative who started a fundraising campaign to find him**, and submit their full name.

Flag format: `Name Surname`

## Recon

From the previous steps the target is fully profiled: **Anthony Michael Ginnetti** ("Tony"),
a former missing person tied to the Columbus, Ohio area, with known handles `buckeyeboi87`,
`whtboi2real100`, and Facebook `KrzWhtboy`.

Pivoting from the person to the *event* (a missing-person case) surfaces the family's public
appeals. A search for the case shows the disappearance was worked heavily on social media by a
relative:

* A LinkedIn "MISSING" appeal states the 34-year-old **Anthony M. Ginnetti** went missing in the
  early hours of **October 30, 2021**, posted by his aunt, who signs off as *"Anthony's Aunt/Mom,
  Libby Ginnetti."*

That gives the likely organizer, but the challenge asks specifically about a **fundraising
campaign**, so the appeal alone isn't enough — I need the actual fundraiser and its listed
organizer.

## Exploit, step by step

```bash
# 1. Pivot from the target to the missing-person event:
#    search:  "Anthony Ginnetti" missing fundraiser GoFundMe
#
# 2. A relative's public "MISSING" appeal identifies the aunt: Libby Ginnetti.
#
# 3. Narrow specifically to the fundraising campaign for the search:
#    search:  "Anthony Ginnetti" missing GoFundMe find organizer
#
# 4. The GoFundMe campaign surfaces:
#    Title:      "Bring Tony Home"   (Tony = Anthony "Michael Anthony" Ginnetti)
#    Organized by: Libby Ginnetti
#
# 5. Cross-check the relationship: Libby self-identifies as Anthony's aunt in her
#    own appeal, confirming she is the relative who started the campaign.
```

The campaign **"Bring Tony Home"** was created by **Libby Ginnetti**, Anthony's aunt — the relative
who launched the fundraiser to find him.

> Format note: the challenge wants the bare `Name Surname`. The campaign and her public profiles all
> use **Libby Ginnetti**, so submit that. "Libby" is a diminutive of *Elizabeth* (public records
> list her as "Elizabeth M Ginnetti"), so if the platform rejects the nickname, `Elizabeth Ginnetti`
> is the only sensible fallback — but the campaign's own attribution is "Libby Ginnetti".

## Flag

```
CCIT{****************}
```

## What I learned

* **Pivot from the person to the event.** Once a target is profiled, the fastest route to
  case-specific facts (fundraisers, appeals, reports) is searching the *incident* — here, the
  missing-person case — rather than the name alone.
* **Fundraising platforms attribute the organizer publicly.** A campaign title plus its
  "organized by" line hands you both the effort and the person behind it in one hit — exactly the
  relative the challenge asks for.
* **Corroborate the relationship before submitting.** The aunt's own "MISSING" appeal confirms the
  family tie, so the fundraiser organizer and "Anthony's relative" are provably the same person.
* **Respect the passive-OSINT rules.** The organizer's name is public, self-published metadata on a
  fundraiser — no contact with targets or relatives is needed, keeping the investigation within the
  series' passive-only constraints.