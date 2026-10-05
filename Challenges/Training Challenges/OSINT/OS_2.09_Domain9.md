# OS_2.09 — Domain 9

---

## Problem description

Ninth challenge in the "Domain" series. It asks to identify the **mobile phone manufacturer** historically used by `libero.it` employees for sending corporate emails.

Flag format: `<manufacturer>`.

## Recon

To prevent spoofing and ensure legitimate email delivery, organizations publish **Sender Policy Framework (SPF)** policies within DNS `TXT` records (`v=spf1 ...`).

Historically, enterprise mobile devices (specifically BlackBerry devices using the BlackBerry Enterprise Server / BlackBerry Internet Service routing architecture) routed outbound emails through proprietary relay servers. For recipient mail servers to accept these emails without failing SPF checks, organizations had to authorize the vendor's outbound relays directly inside their SPF record using an `include:` mechanism (e.g., `include:srs.bis.eu.blackberry.com` or `include:srs.bis.na.blackberry.com`).

By reviewing historical SPF records of `libero.it`, we can identify which smartphone ecosystem was authorized for corporate outbound mailing.

## Solution, step by step

1. Navigate to **[SecurityTrails](https://securitytrails.com/)**.
2. Query `libero.it` and open the **Historical Data $\rightarrow$ TXT Records** section.
3. Locate the historical `v=spf1` entries from the early-to-mid 2010s.
4. Inspect the included outbound mail relay delegations:

```text
v=spf1 ip4:213.209.8.0/21 ... include:srs.bis.eu.blackberry.com ... -all

```

5. The authorized relay domain `blackberry.com` corresponds directly to the mobile device manufacturer: **`BlackBerry`**..

## Flag

```
****************
```

## What I learned

* **SPF-Based Device & Service Profiling:** Historical SPF `include:` mechanisms provide direct intelligence on past third-party SaaS vendors, mail gateways, and corporate mobile fleets utilized by an organization.
* **Legacy Mobile Email Routing (BES/BIS):** Early enterprise smartphone ecosystems required authorizing centralized vendor infrastructure at the DNS zone level to authenticate outbound mobile emails.
* **DNS History in Corporate Forensics:** Historical DNS records document the decommissioned technological stack of an enterprise across its operational lifetime.