# NS_1.01 — Sanity check

---

## Problem description

We're handed `leopardo.pcapng`, a capture of the suspicious Internet traffic against Leopardo's
public site, plus a SHA-256 to verify against. The challenge walks the attack phase by phase in
packet order; this first level only asks to open the file and look at its **comment**.

Reference hash:

```
9b13b78d404c386c87b269e3d25b28644e4d2708ad4f03c85fc889c7f561395d
```

## Recon

Two moves, that's the whole level.

Hash check first, the actual "sanity" part:

```bash
sha256sum leopardo.pcapng
# 9b13b78d404c386c87b269e3d25b28644e4d2708ad4f03c85fc889c7f561395d  leopardo.pcapng
```

Matches, so the file is intact.

Then the comment. Wireshark → *Statistics → Capture File Properties* shows it at the bottom under
*Comments*. The flag is right there.

## Analysis

The comment isn't a packet, it's file-level metadata. pcapng keeps a file-wide comment in its
**Section Header Block**; the legacy `.pcap` format has no field for one. That's the only reason
"just look at the file comment" is a thing here.

## Exploit, step by step

Verify the hash:

```bash
sha256sum leopardo.pcapng
```

Read the comment:

```bash
capinfos leopardo.pcapng | grep -i comment
```

Or in the GUI: *Statistics → Capture File Properties → Comments*.

## Flag

```
CCIT{****************}
```

## What I learned

- pcapng stores a file-wide comment in the SHB; `capinfos` prints it and *Capture File
  Properties* shows it. Plain `.pcap` can't carry one.
- A capture file can hand you data that lives in no packet at all. Worth checking the file
  metadata before diving into the traffic.
