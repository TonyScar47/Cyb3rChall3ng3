# OS_1.12 — Missing people 12

---

## Problem description

Twelfth challenge in the "Missing people" series. The objective is to identify Anthony's most recently known address from historical registry records matching the baseline checkpoint of the investigation.

Flag format: `write only street number and street name as stated on google maps` (e.g., `1106 W Bell Rd`).

## Recon

Building upon the identification criteria established in challenge **OS_1.11**, public record aggregators such as **FastPeopleSearch** compile chronological histories of residential properties, voter registration data, and utilities connected to a target's identity.

Because public registries dynamically append new post-disappearance records (such as secondary forwarding data or property transitions), a target profile may list multiple previous and current addresses. To satisfy the platform's exact flags, historical evaluation of the primary residential locations associated with the target's baseline tracking timeline in Phoenix must be isolated.

Furthermore, access to these platforms requires an active **VPN connection routing through a United States server** to bypass European geo-blocking parameters.

## Solution, step by step

1. Initialize a secure **VPN session with a U.S. exit node** to circumvent the data broker firewall blocks.
2. Open the verified profile for **Anthony Ginnetti (Age 39)** on **[FastPeopleSearch](https://www.fastpeoplesearch.com/)**.
3. Scroll to the **Address History** / **Previous Addresses** inventory to identify established residential nodes within the Phoenix metropolitan sector.
4. Locate the core historical residence listed on the dossier:

```text
1106 W Bell Rd
Phoenix, AZ 85023

```

5. Cross-reference the syntax against Google Maps to verify standard abbreviated designations for the thoroughfare (`W Bell Rd`).
6. Isolate exclusively the street number and street name components: **`1106 W Bell Rd`**.

## Flag

```
****************
```

## What I learned

* **Chronological Discrepancies in Data Baselines:** CTF challenges tracking real-world or simulated targets frequently align with a static historical snapshot. When multiple addresses populate an OSINT record, evaluating previous persistent addresses alongside recent ones is vital to reconcile the platform checker.
* **Geographic Proximity Profiling:** Tracking targets across the same administrative region (Maricopa County / Phoenix infrastructure) ensures logical continuity across consecutive multi-part pivoting tasks.
* **GIS Notation Invariance:** Validating precise spatial formatting directly against global mapping providers ensures compliance with syntax variations involving cardinal points (`W` vs `West`) and roadway type identifiers (`Rd` vs `Road`).