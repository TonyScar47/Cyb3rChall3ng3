# OS_2.02 — Domain 2

---

## Problem description

Second challenge in the "Domain" series. It asks to identify the **online ticket system / helpdesk software** used by `libero.it` for internal assistance.
Flag format: only the name of the company/product without subdomain and TLD (e.g., `zendesk`, not `mail.zendesk.com`).

## Recon

The intuitive initial approach for this challenge was subdomain enumeration to spot an internal portal like `helpdesk.libero.it` or `servicedesk.libero.it`. However:

1. `crt.sh` timed out and crashed with PostgreSQL query errors due to the massive volume of certificates under `%.libero.it`.
2. Free web profilers (like HackerTarget) capped the output at 50 records, truncating the list at letter `J` (`jumborelay.libero.it`).

Instead of brute-forcing large subdomain lists, a cleaner OSINT approach is analyzing the domain's **SPF (Sender Policy Framework)** records. Cloud ticketing platforms (Zendesk, ServiceNow, Freshdesk) send notification emails on behalf of the customer's domain, requiring explicit authorization inside the root domain's DNS **TXT** entries.

## Solution, step by step

1. Navigate to **[MxToolbox SuperTool](https://mxtoolbox.com/SuperTool.aspx)**.
2. Select **TXT Lookup** from the dropdown menu and search for `libero.it`.
3. Inspect the returned TXT records to find the SPF policy string:

```
"v=spf1 ip4:213.209.8.0/21 ip4:213.209.6.249/32 ip4:213.209.17.209/32 ip4:213.209.17.246/32 ip4:213.209.27.51/32 ip4:213.209.27.52/32 ip4:195.140.184.104/29 ip4:195.140.184.112 ip4:195.140.184.231/32 ip4:195.140.184.232/29 ip4:195.140.184.240/29 ip4:141.206.150.96/29 ip4:141.206.150.48/29 include:mail.zendesk.com include:_oxspf.libero.it -all"

```

The SPF record includes an external mail delegation rule:

```
include:mail.zendesk.com
```

4. The vendor is **Zendesk**. Following the flag instructions, strip both the subdomain (`mail.`) and the TLD (`.com`) to extract the clean name: `zendesk`.

## Flag

```
****************
```

## What I learned

* **Subdomain enumeration isn't always the best path:** On high-traffic enterprise domains, public certificate transparency logs often time out and free online scanners truncate results.
* **SPF records expose SaaS integrations:** Third-party ticketing, CRM, and IT helpdesk platforms almost always leave public traces in the domain's SPF `include:` rules to authorize their outbound mail servers.
* **Web-based DNS aggregators:** Tools like MxToolbox SuperTool allow quick extraction and inspection of TXT and SPF records without terminal tools or active target probing.