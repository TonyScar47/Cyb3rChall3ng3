# NS_2.01 — Secret web server

---

## Problem description

We're given `s3cret.pcapng`, traffic captured "from CCIT HQ". No hint about what to look
for: the challenge is to figure out, from the dump alone, where the flag is.

## Recon

*Statistics → Protocol Hierarchy* shows almost everything is TLS on port 443 — plain
browsing to cyberchallenge.it, google, youtube. Encrypted, unreadable, set aside.

*Statistics → Conversations* surfaces a couple of non-web endpoints: `127.0.0.1` and
`172.23.0.1`. The loopback traffic looks promising at first, but *Follow TCP Stream* on it
shows it's just **TabNine** (the editor's autocomplete talking to its local model), not the
server:

```
{"version":1,"kind":"LocalModelDownloadState", ... "path":".../TabNine"}
```

Dead end. So `127.0.0.1` here is local noise, not the target.

## Analysis

The right move is to stop reasoning by IP/port and look for **cleartext HTTP anywhere** in
the capture. Display filter:

```
tcp contains "HTTP/1.1"
```

The only real hit is on `172.23.0.1`, **port 22**, answering with `X-Powered-By: Express`
and a `Host: 172.23.0.1:22` header. In other words, port 22 is not SSH here — it's an HTTP
web server. That's the whole point of the challenge: Wireshark dissects port 22 as SSH by
default, so unless you look for the HTTP verbs directly (or re-dissect the port), the server
stays invisible.

The index page loads two images:

```html
<h1>CCIT secret vault: access granted!</h1>
<img src="data.jpg" alt="CC">
<img src="not_the_flag.jpg" alt="Not the flag">
```

One real, one decoy (`not_the_flag.jpg` is a hint in itself).

## Exploit, step by step

Find the cleartext HTTP:

```
tcp contains "HTTP/1.1"
```

Tell Wireshark to treat port 22 as HTTP: right-click a packet on port 22 → **Decode As…** →
set port 22 to **HTTP**. Now the traffic is dissected as HTTP.

Extract the images: **File → Export Objects → HTTP**. `data.jpg` and `not_the_flag.jpg`
appear in the list — save `data.jpg`.

Open `data.jpg`: the flag is written across the top of the image.

## Flag

```
CCIT{****************}
```

## What I learned

- A service isn't defined by its port. HTTP on 22 is perfectly valid and is exactly what
  this challenge plays on. In Wireshark you need `Decode As → HTTP`, otherwise port 22 stays
  dissected as SSH and you see nothing.
- For pulling files out of traffic, *Export Objects → HTTP* is the direct route — no manual
  carving needed.
- `127.0.0.1` in a capture can be pure local noise (TabNine here). Read it with *Follow
  Stream* before writing it off, don't assume it's the target.