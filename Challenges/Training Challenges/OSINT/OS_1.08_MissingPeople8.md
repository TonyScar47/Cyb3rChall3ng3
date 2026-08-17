# OS_1.08 — Missing people 8

---

## Problem description

Eighth challenge in the OSINT "Missing people" series. Back on the main target, the task is to find
**Anthony Ginnetti's Pinterest profile** and submit it as a username-based URL.

Flag format: `https://www.pinterest.com/USERNAME/`

## Recon

Searching Pinterest for "Anthony Ginnetti" is noisy — the name is shared by many people, and a
handful of same-name Pinterest accounts show up:

`anthonyginnetti`, `anthonyginnetti1991`, `aginnetti0185`, `atginnetti`, `aginnetti33b`,
`ginnettianthony1`, `afghunt1960`, `tbone181960`, `aginnetti19`, `fginnettijr`, `tonyginnetti87` …

None of these can be picked blindly — the right one has to be tied to *our* Anthony, using the
identity established in the earlier levels.

Known fingerprints of the target from previous challenges:

* Instagram `buckeyeboi87` (empty alt) and `whtboi2real100`
* Facebook `KrzWhtboy`; Twitter `Buckeyeboi2113`
* Ohio State fan ("buckeye"), Groveport/Columbus OH, worked at Tim Hortons
* Goes by the nickname **Tony** (cf. the "Bring Tony Home" fundraiser)

The recurring personal signature across his handles is **Tony/buckeye + the number 87**.

## Exploit, step by step

```text
# 1. Aggregate all Anthony Ginnetti profiles in one place (people-search engine, e.g. IDCrawl),
#    which lists ~11 Pinterest accounts for the name.

# 2. Filter to OUR Anthony using his cross-platform signature:
#      - nickname "Tony"
#      - the number "87" (same as Instagram buckeyeboi87)

# 3. Exactly one Pinterest username matches both:
#      tonyginnetti87   =  Tony + Ginnetti + 87

# 4. The other same-name accounts (aginnetti0185, atginnetti, anthonyginnetti1991, ...) belong to
#    unrelated Anthony Ginnettis across the US and carry none of his personal markers.
```

The Pinterest profile that carries his personal signature (**Tony** + **87**, matching
`buckeyeboi87`) is `tonyginnetti87`.

## Flag

```
****************
```

## What I learned

* **Disambiguate by cross-platform signature, not by name.** With a dozen same-name accounts, the
  deciding factor is a personal marker that repeats across platforms — here, "Tony" + "87" (from
  `buckeyeboi87`) — rather than the display name, which every decoy shares.
* **People-search aggregators collapse the noise.** A single IDCrawl-style page lists every
  Instagram/Twitter/Facebook/Pinterest handle for the name at once, making the matching handle easy
  to spot instead of guessing profile-by-profile.
* **Numbers in usernames are identity glue.** A recurring number ("87") ties otherwise different
  handles to the same person and is often the cleanest link between accounts on different platforms.
* **Mind the flag format.** Pinterest profile URLs need the trailing slash, so
  `/tonyginnetti87/` — matching the requested `https://www.pinterest.com/USERNAME/` pattern.