# NS_0.04 — Level4 — 3-way handshake

---

## Problem description

Two nodes need L3 connectivity on the same subnet. Once they can talk, `level4` (run on node1)
fires a TCP handshake at node2 and dumps the packets. Reading the handshake correctly is what
gives the flag.

## Recon

The interfaces come up without an address. Instead of assuming `eth0`, I check which interface
has no `inet` line and configure that one:

```bash
docker exec -it network-node1-1 /bin/bash
ip addr        # find the interface with no inet (i.e. no IP yet)
```

## Exploit, step by step

node1, assign `10.0.0.1` on the side facing node2:

```bash
ip addr add 10.0.0.1/24 dev eth1
ip link set eth1 up
ip addr show eth1          # inet is now set
```

node2, in a new terminal:

```bash
docker exec -it network-node2-1 /bin/bash
ip addr
ip addr add 10.0.0.2/24 dev eth0
ip link set eth0 up
```

Verify the link, then run the checker on node1:

```bash
ping -c 2 10.0.0.1         # from node2: link is up
level4                     # on node1: captures the handshake
```

## Analysis — reading the 3-way handshake

`level4` prints a tcpdump-style trace of node1 trying to open a TCP connection to node2's SSH
port:

```
1) 10.0.0.1.2799 > 10.0.0.2.ssh : Flags [S],  seq 2254
2) 10.0.0.2.ssh  > 10.0.0.1.2799: Flags [S.], seq 1944328249, ack 2255
3) 10.0.0.1.2799 > 10.0.0.2.ssh : Flags [R],  seq 2255
```

Line by line:

- **[S] = SYN** — node1 (`10.0.0.1`, ephemeral source port `2799`) opens the connection to node2.
  The `IP.port` format matters: `10.0.0.2.ssh` means node2, port `ssh` = **22** (tcpdump prints
  the service name for well-known ports instead of the number).
- **[S.] = SYN-ACK** — node2 answers. The dot after the `S` is the ACK flag. Its `ack 2255` is
  node1's `seq` (2254) + 1: the sequence number it expects next.
- **[R] = RST** — node1 resets instead of sending the final ACK, so the handshake never
  completes.

Reading the flag out of this: the **ephemeral port** is the number on the left (`2799`), `ssh`
**converts to its port number** (22), and the **ACK** is the response whose sequence number is
what the other side expects (peer `seq` + 1).

## Flag

```
CCIT{****************}
```

(built from the handshake fields: ephemeral port, `ssh` as a number, the seq/ack relationship)

## What I learned

- `ip addr` first, then configure the interface that has no `inet`. Same "don't assume `eth0`"
  lesson: here `10.0.0.1` goes on node1-`eth1`, not `eth0`.
- tcpdump's `IP.port` notation: the left side is the ephemeral/source port, the right side the
  destination. It prints service names (`ssh`) for well-known ports, so convert back to the
  number (22).
- The flags of a TCP open: `[S]` SYN, `[S.]` SYN-ACK, then normally `[.]` ACK. Here node1 sends
  `[R]` (RST) instead of the final ACK, so the connection is reset, not established.
- The SYN-ACK's `ack` is always the peer's `seq` + 1: the next byte it expects.