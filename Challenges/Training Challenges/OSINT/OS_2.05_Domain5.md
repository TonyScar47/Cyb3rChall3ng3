# OS_2.05 — Domain 5

---

## Problem description

Fifth challenge in the "Domain" series. It asks to identify the **technical contact** listed in past WHOIS data for `libero.it`.

Flag format: `<technical_contact>`.

## Recon

Current WHOIS records for `.it` domains redact personal contact details due to GDPR policies. To retrieve legacy points of contact, we need historical registry snapshots.

Domain intelligence platforms like **Whoxy** store historical registry archives and provide demo interfaces for their historical database API, returning full, structured JSON snapshots of past registrations before privacy redactions took effect.

## Solution, step by step

1. Navigate to **[Whoxy](https://www.whoxy.com/)**.
2. In the **Live Demo** section, click the second green button: **Whois History API**.
3. Enter `libero.it` into the search box and execute the query.
4. Whoxy outputs the raw historical JSON payload containing all 27 archived records.
5. Inspect the historical snapshots (e.g., from 2015 to 2018 in record `num: 2`):

```json
{
  "num": 2,
  "domain_name": "libero.it",
  "query_time": "2015-03-26 00:00:00",
  "create_date": "1999-06-03",
  "technical_contact": {
    "full_name": "Antonio Converti",
    "company_name": "Italiaonline S.p.A."
  }
}
```

6. The unredacted technical contact full name recorded in historical data is **Antonio Converti**.
7. Wrap the result inside the competition flag format: `CCIT{Antonio Converti}`.

## Flag

```
****************
```

## What I learned

* **Whoxy Live Demo API tools:** Navigating to the *Whois History API* demo on Whoxy allows instant querying of full historical timeline data in clean JSON format without paying for API credits or running local scrapers.
* **Tracking domain personnel changes over time:** Historic WHOIS JSON arrays (`whois_records`) expose changes in administrative and technical leadership across different company eras (e.g., Libero Srl $\rightarrow$ Italiaonline S.p.A.).
* **Bypassing privacy redactions:** When current WHOIS lookups mask contacts as `hidden` or `REDACTED FOR PRIVACY`, historical databases preserve the original contact details archived before GDPR enforcement.