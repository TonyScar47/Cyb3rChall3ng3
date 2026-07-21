# Introduction — Network Security

> **Foundations series.** These are the introductory challenges: network-forensics puzzles on
> captured traffic (`.pcap` / `.pcapng`). Rather than solving each capture by hand, I consolidated
> the extraction techniques into a single carver — [`scalper.py`](./scalper.py) — so this
> walkthrough is organized around *what the tool does*, layer by layer.
>
> For the reasoned, in-depth write-ups (including the harder network-forensics track) see the
> [`training/`](../training) section.

**Platform:** CyberChallenge Italy · **Category:** Network Security / Traffic Forensics

Every layer looks for the same universal flag shape: `[a-zA-Z0-9_]+\{.*?\}`.

---

## Layer 1 — Plaintext in packet payloads

**Challenges 01 / 03 / 06.**
The flag travels in the clear inside a packet payload. Read the raw bytes of every packet
(or follow the TCP stream in Wireshark) and regex for the flag pattern.

```python
for pkt in rdpcap("capture.pcapng"):
    for f in FLAG_RE.findall(bytes(pkt)):   
        print(f)
```

## Layer 2 — pcapng metadata (packet comments)

**Challenge 05.**
`pcapng` (unlike legacy `pcap`) has a block structure that can carry **comments** — metadata
that never appears in any payload. The flag hides there, so payload-only scanning misses it.

```python
if getattr(pkt, "comment", None):       
    print(pkt.comment)
```

*(Also visible with `capinfos` or Wireshark ▸ *Packet comments* — this is exactly the block-level
metadata the training NS_1.x forensics track builds on.)*

## Layer 3 — Compressed payloads

**Challenge 08.**
The flag sits inside a **gzip-compressed** payload, so a raw string scan finds nothing. Detect
the gzip magic bytes, decompress from that offset, then search the decompressed data.

```python
if b"\x1f\x8b\x08" in raw:                   
    data = gzip.decompress(raw[raw.find(b"\x1f\x8b\x08"):])
    print(FLAG_RE.findall(data))
```

## Layer 4 — Encrypted traffic (TLS)

**Challenge 09.**
Traffic is TLS-encrypted; the capture ships with an `SSLKEYLOGFILE`. Feed the keys to TShark
to decrypt the session, then grep the decrypted output.

```bash
tshark -r capture.pcapng -o tls.keylog_file:keys.txt -V | grep -oE '[a-zA-Z0-9_]+\{.*\}'
```

*Concept:* encryption isn't a wall if you hold the session keys — the keylog file is what
browsers dump for exactly this kind of debugging/analysis.

## Layer 5 — File carving over HTTP

**Challenge 10.**
The flag was inside a **file transferred over HTTP** (a PNG/JPG/HTML), not in any single packet.
Reassemble and export the transferred objects, then search inside each extracted file.

```bash
tshark -r capture.pcapng --export-objects http,extracted_objects/
# → then scan every carved file for the flag pattern
```

---

## The unified solver

Instead of five separate one-offs, [`scalper.py`](./scalper.py) runs all layers in sequence on a
single capture:

```bash
python scalper.py capture.pcapng [keys.txt]
```

It carves HTTP objects, optionally decrypts TLS with a keylog, decompresses gzip payloads, reads
pcapng comments, and regex-scans raw bytes — reporting any flag it finds at any layer.

> **Honest note:** the only artifact I preserved for this track is the solver, so challenges
> **02, 04, and 07** aren't reconstructed here — the script doesn't encode a distinct step for
> them, and I'd rather leave a gap than invent a solution I can't verify.

---