# OS_1.11 — Missing people 11

---

## Problem description

Eleventh challenge in the "Missing people" series. The objective is to identify Anthony's most probable phone number based on the records and data points accumulated across the investigative lifecycle.

Flag format: `\d+` (raw digits only, excluding international prefixes or local brackets).

## Recon

The investigation pivots from the formal NamUs missing person profile (Case `#MP86351`), which explicitly identifies the target as **Anthony Michael Ginnetti**.

To locate a primary, actively associated telephone record for a U.S. citizen completely for free, public records registries and open-source data brokers provide comprehensive OSINT lookup utilities. However, platforms like **FastPeopleSearch** or **TruePeopleSearch** implement strict geographic restrictions and firewall blocks against European IP addresses due to compliance frameworks (GDPR).

Therefore, establishing an encrypted tunnel via a **VPN with a U.S. exit node** is an absolute technical prerequisite to circumvent the HTTP 403 blocks and query the infrastructure.

## Solution, step by step

1. Initialize a secure **VPN connection routing through a United States server**.
2. Navigate to **[FastPeopleSearch](https://www.fastpeoplesearch.com/)** (or TruePeopleSearch).
3. Input the target identifiers extracted from the official NamUs case files:
* **Name:** `Anthony Ginnetti`
* **City/State:** `Phoenix, AZ`


4. Analyze the returned public record entries. The primary candidate matches perfectly: **Anthony Ginnetti, Age 39**, listing multiple historical and active addresses across the Maricopa County cluster (**Peoria, AZ** and **Phoenix, AZ**).
5. Open the comprehensive profile details via the **"View Free Details"** gateway.
6. Locate the **Phone Numbers** directory and isolate the current mobile entry marked as primary:

```text
(602) 465-5406

```

7. Normalize the string to comply with the requested flag format by stripping the leading country code, local brackets, spaces, and hyphens: **`6024655406`**.

## Flag

```
****************
```

## What I learned

* **Geographic Access Restrictions in OSINT:** U.S. public data aggregators systematically block foreign traffic. Utilizing regional proxy infrastructures or VPN tunnels is mandatory to interact with North American data-broker endpoints.
* **Biographical Cross-Referencing:** Age records in public databases naturally increment over time; cross-referencing the NamUs "Age at Disappearance" baseline against current registry age estimates prevents false positives among same-name candidates.
* **String Normalization for Flag Input:** Aggregated telephone metadata must be scrubbed of regional layout artifacts (parentheses, whitespace delimiters, hyphen separators) to yield a pure programmatic sequence matching strict validation expressions (`\d+`).