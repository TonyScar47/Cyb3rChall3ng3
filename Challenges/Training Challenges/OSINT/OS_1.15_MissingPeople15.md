# OS_1.15 — Missing people 15

---

## Problem description

Fifteenth challenge in the "Missing people" series. It asks to identify the exact brand and model of the sneakers worn by the subject in the provided photograph.

Flag format: `Brand Model`.

## Recon

Visual analysis and Reverse Image Search (RIS) on raw images containing multiple competing visual elements (such as sports apparel, team logos, or background clutter) often pollute neural search embeddings. Search engines tend to prioritize high-contrast graphic overlays (like the Ohio State and Michigan insignias) over the actual footwear.

To achieve high-fidelity matches, the target object must be isolated through precise cropping. Key visual identifiers present on the shoes include:

* A mid/high-top retro basketball silhouette.
* A prominent triangular tongue badge featuring vintage **"Flight"** script lettering.
* Distinctive two-tone upper panelling with a red inner collar lining and a contrast white outsole/midsole unit.

## Solution, step by step

1. Crop the source image tightly around one of the sneakers to eliminate surrounding visual noise and graphic overlays.
2. Submit the cropped footwear crop to **Google Lens** or **Yandex Visual Search**.
3. Identify the triangular tongue emblem as part of the historic **Nike Flight** basketball footwear lineage.
4. Cross-reference the resulting image matches against sneaker databases and archival release listings (*Sneaker News*, *KicksOnFire*, *StockX*).
5. Verify the silhouette, side overlay cuts, perforations, and collar design against the **Nike Air Flight Falcon** (Cool Grey / Team Red colorway).
6. Format the string according to the requested `Brand Model` specification: **`Nike Air Flight Falcon`**.

## Flag

```text
****************
```

## What I learned

* **Targeted Region-of-Interest (ROI) Cropping:** Eliminating irrelevant graphic overlays and high-contrast distractions is essential to prevent visual search algorithms from matching the wrong subject matter.
* **Sub-Brand / Lineage Recognition:** Identifying sub-line branding elements (like Nike’s "Flight" triangle emblem) drastically narrows the search space within extensive manufacturer catalogs.
* **Archival Database Cross-Referencing:** Confirming specific commercial model designations requires validating structural paneling and colorway details against dedicated product registries.