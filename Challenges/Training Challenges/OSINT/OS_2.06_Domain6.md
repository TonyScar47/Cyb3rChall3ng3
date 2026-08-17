# OS_2.06 — Domain 6

---

## Problem description

Sixth challenge in the "Domain" series. It asks to identify which other domain shares the same Google Analytics tracking code as `libero.it`.

Flag format: `<domain>`.

## Recon

Google Analytics tracking codes (such as Universal Analytics IDs formatted as `UA-XXXXXX-Y`) are embedded directly into a website's client-side source code. When organizations deploy common tracking properties across different web assets, this ID acts as a digital fingerprint connecting seemingly separate properties.

Reverse analytics intelligence tools like **AnalyzeID** crawl and index these tracking IDs across the web, allowing analysts to perform reverse lookups and pivot from one known target domain to uncover all co-owned or affiliated domains sharing the same tracking infrastructure.

## Solution, step by step

1. Navigate to **[AnalyzeID](https://analyzeid.com/)**.
2. Enter `libero.it` into the search bar and submit the query.
3. Inspect the detected tracking tags and attributes associated with the domain.
4. Filter by the Universal Analytics ID **`UA-113371876`** to inspect all correlated web properties:

| Confidence | Domain | Google Analytics |
| --- | --- | --- |
| **260%** | `libero.it` | `UA-113371876` |
| **100%** | `tobe.libero.it` | `UA-113371876` |
| **100%** | `wlibero.it` | `UA-113371876` |

5. Discard third-level subdomains (`tobe.libero.it`) to isolate the separate apex domain sharing the exact same tracking code: **`wlibero.it`**.
6. Wrap the discovered domain inside the competition flag format: `CCIT{wlibero.it}`.

## Flag

```
****************
```

## What I learned

* **Reverse Analytics Pivoting:** Google Analytics (`UA-` / `G-`) and AdSense (`pub-`) IDs embedded in HTML sources allow OSINT analysts to pivot across domains and map out corporate web ecosystems managed by the same entity.
* **AnalyzeID Infrastructure Fingerprinting:** AnalyzeID aggregates multiple shared identifiers—including Google Analytics tags, IP clusters, and shared name servers—providing confidence scores for cross-domain relationships.
* **Filtering Noise in Shared Tag Lookups:** Discarding internal subdomains and looking specifically for distinct root domains sharing identical tracking IDs is essential to identifying external satellite or alternative landing sites.