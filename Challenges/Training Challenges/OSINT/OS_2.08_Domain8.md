# OS_2.08 — Domain 8

---

## Problem description

Eighth challenge in the "Domain" series. It asks to identify the **Registrar company name** associated with `libero.it`.

Flag format: `<company_name>`.

## Recon

A live WHOIS lookup on `libero.it` shows modern management details (e.g., `Reevo s.p.a.` under registrar tag `IOL-REG`). However, the challenge targets the historical managing registrar of the domain.

Commercial WHOIS intelligence platforms like **DomainTools** archive past domain records, but lock timeline data behind paywalls. Because these lookup profile URLs follow predictable paths (`[https://whois.domaintools.com/](https://whois.domaintools.com/)<domain>`), we can use the **Wayback Machine (Internet Archive)** to inspect historical web snapshots of past WHOIS queries completely for free.

## Solution, step by step

1. Navigate to the **[Wayback Machine](https://web.archive.org/)**.
2. Enter the standard DomainTools lookup URL for the target:
```text
https://whois.domaintools.com/libero.it

```


3. Open an archived snapshot from the historical archive (e.g., from 2018–2022).
4. Scroll down to the **Registrar** information block:

```text
Registrar
  Organization:   ITnet s.r.l.
  Name:           ITNET-MNT / IOL-REG

```

5. Extract the organization name registered as the managing registrar: **`ITnet s.r.l.`**.

## Flag

```
****************
```

## What I learned

* **Bypassing Paywalled WHOIS History via Archive.org:** The Wayback Machine regularly indexes public WHOIS aggregators (like DomainTools), providing a free, reliable alternative to commercial historical WHOIS subscriptions.
* **Maintainer / Registrar Evolution in `.it`:** Historic Italian domain records used the Maintainer (`MNT`) tag (`ITNET-MNT` $\rightarrow$ `IOL-REG`), registering `ITnet s.r.l.` as the technical infrastructure entity for the Libero/Wind group.
* **Correlating Corporate Lineage:** Historical registrar tracking provides insight into parent-company migrations and infrastructure providers across different corporate restructuring phases.