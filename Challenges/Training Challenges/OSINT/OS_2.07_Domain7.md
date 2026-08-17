# OS_2.07 — Domain 7

---

## Problem description

Seventh challenge in the "Domain" series. It asks to identify the most recent **Google Site Verification code** registered inside the DNS `TXT` records for `libero.it`.

Flag format: `<code>`.

## Recon

Google Search Console and Google Workspace require webmasters to prove domain ownership by deploying a unique token into the domain's DNS `TXT` zone file in the format:

```text
google-site-verification=<verification_token>

```

Large, long-standing domains like `libero.it` often accumulate multiple verification tokens over time as different internal teams, services, or migration processes register properties. By querying current DNS zone data with tools like **DNSChecker** or native command-line utilities (`dig`), analysts can enumerate all active tokens and cross-reference them chronologically (e.g., via historical DNS archives like **SecurityTrails**) to isolate the newest entry.

## Solution, step by step

1. Navigate to **[DNSChecker](https://dnschecker.org/all-dns-records-of-domain.php)** or open a local terminal.
2. Enter `libero.it` as the target domain and select the **TXT** record type (or execute `dig TXT libero.it +short`).
3. Inspect the returned TXT records and filter for entries starting with `google-site-verification=`.
4. Four distinct active verification tokens are returned:
* `Uhj3hk68gf5xSOTkWZsxeUYymAtnGCEa5qzQwgvKato`
* `rwDHe3W-KaW0jUSCtpGSk5UWBkwhAOpw2mQdmn4NQLw`
* `Uqlsuq5lYki3ePd2jAK3xSCEO-hUADPiA093XneooE4`
* `fqsYdy3wwvDP-i736PKI7o6xfl203FX5pvS53EyScLM`


5. Check the addition timeline (via historical DNS records on **SecurityTrails** under *Historical Data $\rightarrow$ TXT Records* or zone updates) to determine the latest registered entry.
6. The most recently registered verification token is **`fqsYdy3wwvDP-i736PKI7o6xfl203FX5pvS53EyScLM`**.

## Flag

```
****************
```

## What I learned

* **DNS TXT Ownership Verification:** Web services rely on arbitrary DNS TXT tokens (`google-site-verification`, `have-i-been-pwned-verification`, etc.) to authenticate administrative domain ownership.
* **Managing Multiple Legacy DNS Tokens:** Production domains often retain legacy verification hashes from past infrastructure setups; comparing timestamps or historical first-seen dates is necessary to distinguish modern records from deprecated ones.
* **DNS Zone Enumeration:** Utilities like `dig` and online DNS lookup engines provide immediate access to all publicly published verification hashes and security policies (SPF, DKIM, DMARC).