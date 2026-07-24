# NS_1.03 — Well-hidden ports

---

## Problem description

Leopardo claims the web host runs nothing but a web server, and that any other service left running
by accident wouldn't expose useful data. The level asks whether that's true.

## Recon

Target is `1.1.122.222`. To find which ports actually answered, the useful signal isn't the SYNs
the attacker sent — anyone can send those to any port — but the replies. A port that answers with
SYN/ACK is open; a RST means closed:

```
tcp.flags.syn == 1 && tcp.flags.ack == 1
```

Adding the server's source port as a column (right-click *Source Port → Apply as Column*) and
reading the rows where Source is `1.1.122.222`, four ports reply:

**80**, **443**, **5432**, **10000**.

So no, it isn't just a web server. Two of those aren't what their number suggests:

- **5432** is the PostgreSQL port, but the responses read `Server: Apache/2.4.18 (Ubuntu)` and the
  error-page footer literally says `... Port 5432`. It's a second web server on a database port.
- **10000** answers `Server: MiniServ/1.920` — Webmin, an admin panel.

That answers the first half. The second half — "does it expose useful data?" — needs a look at what
the hidden Apache on 5432 actually serves.

## Analysis

Since 5432 is a real web server, it has the usual web files, including a per-site `robots.txt`.
One wrinkle first: Wireshark decodes port 5432 as PostgreSQL, so `http.*` filters don't apply to it
out of the box. Right-click a 5432 packet → *Decode As… → HTTP*, and the HTTP machinery (filters,
Follow HTTP Stream, gzip inflation) starts working. Then pull the robots file:

```
http.request.uri == "/robots.txt"
```

One request at t≈102s to `www.leopardocompany.com:5432`. *Follow → HTTP Stream* (the response is
gzip, Wireshark inflates it in the Follow view once the port is decoded as HTTP) gives two lines:

```
Disallow: Q0NJVHs4ZGNkNmVmZC01YzgxLTRmM2MtOWQ3My02Y2MyNWJmMWJlNzZ9
Disallow: ~administrator
```

Neither is a real path. The first is base64 — it begins `Q0NJVHs`, which is `CCIT{` encoded, so
it's the flag:

```bash
echo Q0NJVHs4ZGNkNmVmZC01YzgxLTRmM2MtOWQ3My02Y2MyNWJmMWJlNzZ9 | base64 -d
# CCIT{...}
```

So the "switched-off, nothing-useful" service on port 5432 is a live Apache that hands out a flag
in a world-readable file. That's the useful data being exposed, and it's the answer to the level:
the claim doesn't hold.

(The second line, `~administrator`, points at a hidden Apache `UserDir` — the attacker requested
`/~administrator/` right after reading `robots.txt` at t≈120s. That thread continues in the next
level.)

## Exploit, step by step

Find the open ports:

```
tcp.flags.syn == 1 && tcp.flags.ack == 1
```

Decode port 5432 as HTTP (*Decode As… → HTTP*), then read `robots.txt`:

```
http.request.uri == "/robots.txt"
```

*Follow → HTTP Stream*, then base64-decode the `Disallow` value (CyberChef `From Base64`, or
`base64 -d`). If you'd rather not touch the dissector, `frame contains "robots"` finds the same
request in the raw bytes.

## Flag

```
CCIT{****************}
```

## What I learned

- SYN/ACK is the answer, not the question. `tcp.flags.syn == 1 && tcp.flags.ack == 1` pulls the
  open ports out of a whole scan in one filter, and the source port column tells you which they are.
- A port number is a hint, not a fact. 5432 reads as PostgreSQL, but the server banner said Apache.
  "Nothing but a web server" was already false, and the extra web server was the interesting one.
- The useful data a "harmless" service exposes can be as simple as a `robots.txt`. A live web
  server on an unexpected port still serves its standard files to anyone who asks.