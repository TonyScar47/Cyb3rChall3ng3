# NS_0.03 — Level3 — One well-known and one …

---

## Problem description

Same node, two services this time: one on a well-known port, one somewhere a default scan won't
look. You have to find both and read what they serve.

## Recon

A default `nmap` (top 1000 ports) only shows the well-known one. Forcing the full range exposes
the second port up in the non-standard range.

## Exploit, step by step

```bash
docker exec <name> hostname -I
ssh root@<ip>
nmap -p- <ip>                     # all 65535 ports, not just the top 1000
```

Then open both ports in the browser and read each page:

```
http://<ip>:<well_known_port>
http://<ip>:<high_port>
```

## Flag

```
CCIT{****************}
```

## What I learned

- The default `nmap` scans the top 1000 ports only. The non-well-known service was up in the
  high range and only showed with `-p-`. A "nothing else open" result from a default scan
  doesn't mean there's nothing else.