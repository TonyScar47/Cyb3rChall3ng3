# NS_1.04 — We are the robots

---

## Problem description

A web server can run several sites on several ports, and `robots.txt` is a standard file. The level
asks what could go wrong and whether the attacker exploited the discovered evidence.

## Recon

From the previous level, the `robots.txt` on port 5432 disclosed a hidden path (`~administrator`),
and the neighbouring `~admin2` UserDir exists too. The attacker didn't stop at reading them by
hand — at t≈205s there's an automated **`nmap -sV` service scan** against 5432, recognisable from
its probes: `GET /nmaplowercheck<epoch>`, `POST /sdk` (a vSphere SOAP body), and `HEAD` requests
against user directories (`/~root`, `/~admin`, `/~admin2`). `robots.txt` had disclosed that the
UserDir feature was on (`~administrator`); the scan probes neighbouring names from there.

The flag rides along in that scan. The obvious filter, though, returns nothing:

```
http.user_agent contains "CCIT"      <- zero packets
```

## Analysis

The reason is the dissector. Wireshark picks it by port number, and 5432 is registered as
PostgreSQL, so those packets never reach the HTTP dissector and no `http.*` field exists on them —
the filter can't match a field that isn't there. Searching the raw bytes ignores dissectors
entirely:

```
frame contains "CCIT"
```

That returns five packets. Four are `1.1.122.1 → 1.1.122.222` at t≈205s (the attacker's scan); the
fifth is the reverse direction and much later, so it belongs to a different phase. Picking one of
the attacker's packets and *Follow → TCP Stream* shows the request and its User-Agent:

```
GET /nmaplowercheck1584963974 HTTP/1.1
User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0 CCIT%7B37be0fff-...%7D
Host: www.leopardocompany.com:5432
```

The same flag-bearing User-Agent is on all the scan probes at that timestamp (`/nmaplowercheck`,
`POST /sdk`, `HEAD /`, `HEAD /~admin2`). It's the scanner's own header — attacker-controlled — and
it's URL-encoded (`%7B` = `{`, `%7D` = `}`).

## Exploit, step by step

Search the bytes rather than the parsed fields (the http filter won't work on port 5432):

```
frame contains "CCIT"
```

Pick a match going `1.1.122.1 → 1.1.122.222` and *Follow → TCP Stream*. Read the `User-Agent:`
line — the flag is the string appended after `Firefox/74.0`.

URL-decode it (CyberChef `URL Decode`, or replace `%7B`→`{` and `%7D`→`}` by hand).

## Flag

```
CCIT{****************}
```

## What I learned

- Wireshark chooses its dissector by port number. Apache answering on 5432 got parsed as
  PostgreSQL, so `http.user_agent` didn't exist on those packets and my filter matched nothing.
  `frame contains` searches the bytes and doesn't care; *Decode As… → HTTP* is the proper fix.
- The User-Agent is fully attacker-controlled and appears on every probe a scanner sends. Here it
  carried the flag; in a real case it's a reliable way to fingerprint the tooling behind a scan.
- Direction matters when a search returns several hits. Client → server is what the attacker sent;
  the flag was in the attacker's own request, not in anything the server replied with.