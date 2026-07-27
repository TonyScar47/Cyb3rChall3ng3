# NS_2.06 — IPV-4

---

## Problem description

A single file, `ipv-4.pcapng`. The challenge text is the explanation dressed up as a brag: "I solved IPv4 address exhaustion by using negative addresses." Meaning: somewhere there are "negative IPs", and they're the key.

## Recon

Monotone hierarchy: 410 frames, all **DNS over UDP**, nothing else. Looking at the queries:

```
dns.flags.response==0
```

```
192.168.0.-1   type 16
192.168.0.-2   type 16
192.168.0.-3   type 16
...
```

Two things jump out right away. First: the requested names are `192.168.0.-N`, with the last octet **negative**. That's not a valid IP (an octet is 0-255), so it isn't an address, it's a string built on purpose. Second: `type 16` is **TXT**, not A. So we're not resolving names into addresses, we're pulling out text.

Looking at the TXT responses:

```
dns.flags.response==1 && dns.txt
```

```
192.168.0.-10    flag=CCIT{
192.168.0.-130   flag=st
192.168.0.-50    flag=a_
192.168.0.-30    flag=v-
...
```

Each TXT is a `flag=` with two characters. Seventeen pieces in total.

## Analysis

The `-N` is an **order index**, not an address. The brag about "negative addresses" was literal: the author stuffed a counter into the final octet with a minus sign in front, so it looks like an IP but it's just `-10, -20, -30, ...`.

The catch is that in the pcap the packets are **not** in index order: they come `-10`, then `-130`, then `-50`, then `-30`. Concatenate in capture order and you get garbage. They have to be reordered by the number after the dash.

Here there's a trap that bites you in Wireshark. If you add `dns.qry.name` as a column and sort by clicking it, the sort is **lexicographic on the string**, not numeric: `-10` comes before `-20`, fine, but `-100` comes before `-20` (because "1" < "2" as characters). Result: wrong order and a scrambled flag. I noticed because after `CCIT{` I was getting random junk. The fix is to sort **numerically** on the index, not alphabetically.

## Exploit, step by step

Isolate the TXT responses and extract name and content:

```bash
tshark -r ipv-4.pcapng -Y "dns.flags.response==1 && dns.txt" \
  -T fields -e dns.qry.name -e dns.txt
```

Strip the `192.168.0.-` prefix and the `flag=`, sort numerically on the index, concatenate:

```bash
... | sed 's/192\.168\.0\.-//; s/flag=//' | sort -n -u | awk '{f=f $2} END{print f}'
```

Ordered by index, the pieces are:

```
10 CCIT{  20 ip  30 v-  40 4_  50 a_  60 n3  70 w_  80 b3  90 au
100 ti  110 fu  120 l_  130 st  140 an  150 da  160 rd  170 }
```

Concatenated:

```
CCIT{ipv-4_a_n3w_b3autiful_standard}
```

"IPv-4, a new beautiful standard", matching the opening brag.

## Flag

```
CCIT{****************}
```

## What I learned

- An IP octet out of range (`-1`, or `>255`) in a `dns.qry.name` field is the signal that it's not an address but a string built ad hoc: the data is in the *name*, not the routing.
- `type 16` = TXT. When DNS queries aren't A/AAAA but TXT, the payload is arbitrary text exfiltrated over DNS. It's a real tunneling/exfil technique, here in toy form.
- Column sorting in Wireshark on a string field is lexicographic. `-100` ends up before `-20`. The flag coming out in pieces after `CCIT{` reminded me: for numeric indices you sort as a number, not as text.
- The packets in the pcap aren't in logical order: capture order isn't data order. The ordering comes from the content (the index), not the position in the file.