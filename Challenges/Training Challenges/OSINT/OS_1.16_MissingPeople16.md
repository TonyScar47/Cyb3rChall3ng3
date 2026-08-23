# OS_1.16 — Missing people 16

---

## Problem description

Sixteenth challenge in the "Missing people" series. It asks to determine the original name tattooed on Anthony's neck prior to being covered up by a rose motif, using the hint that the tattoo refers to one of his ex-girlfriends.

Flag format: `Name`.

## Recon

In many criminal justice and OSINT investigations, subjects alter or cover identifiable body modifications (such as names of former associates or partners) with darker, denser cover-up tattoos (e.g., floral motifs or solid blackout work). Historical booking photos and incarceration intake mugshots capture physical appearances at specific points in time, preserving obsolete or subsequently altered markings.

Examining the provided high-resolution historical intake photo reveals:

* An old cursive/script tattoo located on the right side of the subject's neck (viewer's lower-left).
* The lower section of the word is occluded by the crew-neck collar line.
* The exposed upper glyphs clearly reveal the ascenders, loops, and descenders of the lowercase suffix: **`...berly`** (distinct `b`, `e`, `r`, `l`, `y`).

## Solution, step by step

1. Inspect the provided historical booking image in full resolution.
2. Focus visual analysis on the neck area above the collarline to locate pre-cover-up ink.
3. Transcribe the visible cursive glyphs emerging from beneath the shirt collar: **`-b-e-r-l-y`**.
4. Analyze the spatial constraint of the remaining hidden letters between the start of the neck curve and the letter `b` (accounting for approximately 3 letters: `K-i-m`).
5. Reconstruct the complete female given name matching the morphological pattern and prompt context: **`Kimberly`**.
6. Format the string according to the requested `Name` specification: **`Kimberly`**.

## Flag

```text
****************
```

*(o `Kimberly` a seconda del wrapper richiesto)*

## What I learned

* **Historical Intake Image Mining:** Booking photo archives serve as critical temporal records for tracking physical modifications, identifying tattoos before later alterations or cover-ups.
* **Morphological Glyph Reconstruction:** Deciphering partially obscured script tattoos relies on analyzing character ascenders, descenders, and character spacing (kerning) relative to the concealing boundary.
* **Onomastic Pattern Matching:** Combining visible phonetic suffixes (such as `-berly`) with prompt constraints (ex-partner names) allows rapid disambiguation of partially occluded textual evidence.