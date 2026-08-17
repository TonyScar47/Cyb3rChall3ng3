# OS_2.10 — Domain 10

---

## Problem description

Tenth challenge in the "Domain" series. It asks to determine the exact timestamp when `libero.it` was registered for the first time.

Flag format: `YYYY-MM-DD HH:MM:SS`.

## Recon

To inspect registration lifecycles, registrar delegation, and ownership metadata of an Internet resource, registries provide public directory queries via the **WHOIS** protocol.

For the `.it` country code top-level domain (ccTLD), the authoritative entity is **Registro .it** (operated by IIT-CNR). When querying authoritative WHOIS databases or domain intelligence tools, the domain's initial delegation is recorded in the `Created:` field.

By performing a WHOIS lookup against `libero.it`, we can directly retrieve the original registration timestamp.

## Solution, step by step

1. Navigate to **[DomainTools Whois](https://whois.domaintools.com/)** (or run `whois libero.it` in a terminal).
2. Query the target domain: `libero.it`.
3. Locate the authoritative **Whois Record** section.
4. Inspect the domain lifecycle metadata:

```text
Domain:             libero.it
Status:             ok
Signed:             no
Created:            1999-06-03 00:00:00
Last Update:        2026-06-19 00:51:22
Expire Date:        2027-06-03

```

5. Extract the initial creation timestamp matching the requested `YYYY-MM-DD HH:MM:SS` format: **`1999-06-03 00:00:00`**.

## Flag

```
****************
```

## What I learned

* **Authoritative ccTLD WHOIS Lookups:** Country-code top-level domain registries maintain authoritative, immutable registration records containing the exact initial creation timestamp.
* **Field Discrimination in Registry Responses:** Distinguishing between the primary domain-level `Created:` timestamp and subsequent contact/entity-level creation records (`Registrant`, `Admin Contact`) is critical to avoid false positives.
* **Timestamp Formatting Standards:** Legacy `.it` domain records initialize the timestamp component at midnight (`00:00:00`), strictly complying with standard ISO/extended datetime formatting.