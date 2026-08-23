# OS_1.18 — Missing people 18

---

## Problem description

Eighteenth challenge in the "Missing people" series. It asks to determine the full name of Anthony M. Ginnetti's mother.

Flag format: `Name Surname`.

## Recon

Anthony M. Ginnetti was born in July 1987 and has historical records in Peoria and Phoenix, Arizona. Public data aggregator **FastPeopleSearch** indexes background reports containing addresses, associates, and familial ties. However, FastPeopleSearch enforces geo-blocking on European IP addresses due to GDPR compliance, requiring a non-European (US) exit node to access the platform.

## Solution, step by step

1. Connect to a **non-European VPN** (e.g., United States) to bypass the regional geo-restriction on FastPeopleSearch.
2. Navigate to `fastpeoplesearch.com` and search for **`Anthony Ginnetti`** in **`Peoria, AZ`**.
3. Open the background report for the profile matching the birth date of July 1987.
4. Scroll down to the **Relatives** section and click the **`Show More...`** link to expand the full list of associated family members.
5. Apply generational age filtering (looking for a female relative born ~1947–1969): locate **`Theresa Ginnetti`** (born June 1964, aged 23 when Anthony was born).
6. Format the name according to the flag specification.

## Flag

```text
****************
```

## What I learned

* **Geo-Restrictions in OSINT:** Many US-based public record aggregators block traffic from European IP ranges due to GDPR; maintaining access through US proxies/VPNs is essential for cross-border footprinting.
* **UI Data Truncation:** Aggregators often hide secondary or extended relatives behind UI accordions (e.g., "Show More"), requiring full expansion before concluding a data point is missing.
* **Generational Correlation:** Calculating the physiological age gap (18–40 years older than the target) quickly narrows down mother/father candidates within extensive family trees.