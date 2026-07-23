# NS_0.06 — Level6 — NAT1

---

## Problem description

Three Docker containers (`node1`, `node2`, `node3`) on separate networks. `node1` is
**dual-homed**: one foot on `10.0.0.0/24` (where `node2` lives) and one on `192.168.123.0/24`
(where the destination `192.168.123.1` lives).

Goal: configure **NAT** on a node so `node2` can reach `192.168.123.1`. Verification runs the
`level6` script on `node2`, which prints the flag if everything is in place.

The brief provides the MASQUERADE (source NAT) template:

```
iptables -t nat -A POSTROUTING -o [devicename] --source [sourcenet_ipaddress/netmask] -j MASQUERADE
```

## Recon

After `make up` the three containers are up (`downloads-node1-1`, `downloads-node2-1`,
`downloads-node3-1`).

Fresh out of `make up`, the `node1` and `node2` interfaces are `UP` but have **no IP** (only
`lo` has one). They need manual configuration.

Starting state from `ip addr`:

- `node1` -> `eth0` already has `192.168.123.123/24` (destination side); the other interface has no IP (`10.0.0.0/24` side).
- `node2` -> both interfaces without IP.

### Which interface to use

The container has **two** interfaces (`eth0`, `eth1`) and it's not obvious which sits on which
network. The rule is **inspect before configuring**, never assume `eth0` blind.

To map the virtual cables (veth pairs) I use the `@ifNN` index next to each interface: two
interfaces with the **same** index are the two ends of the same cable.

```bash
# on node1
ip -o link | grep -E 'eth0|eth1'
# on node2
ip -o link | grep -E 'eth0|eth1'
```

Result (one session; the indices change on every `make up`):

| Node  | Interface | Index   |
|-------|-----------|---------|
| node1 | eth0      | `@if26` |
| node1 | eth1      | `@if22` |
| node2 | eth0      | `@if22` |
| node2 | eth1      | `@if23` |

Pairing the indices: **node1-`eth1` <-> node2-`eth0`** (both `if22`) are the two ends of the
same cable. That's the direct `node2 -> node1` link on `10.0.0.0/24`.

> ⚠️ The `@ifNN` indices (and sometimes the veth pairing itself) **change on every `make down`/`make up`**. You can't rely on a mapping from a previous session; reverify every time.

## Analysis

Two things to understand: one about the network, one hidden in the script.

### 1. The return-path problem (why NAT is needed)

Teaching `node2` the route to `192.168.123.0/24` (via `node1`) sends packets **out**, but that
isn't enough. When the packet reaches `192.168.123.1`, its source is `10.0.0.2`. But
`192.168.123.1` **has no route to `10.0.0.0/24`**: it doesn't know how to answer. The reply is
lost and the connection stays half-open.

**MASQUERADE** (source NAT) on `node1` fixes this: when `node1` forwards `node2`'s packets toward
`192.168.123.x`, it rewrites the **source** address with its own IP on that network
(`192.168.123.123`). So `192.168.123.1` replies to an address it can reach (`node1`), and
`node1`, thanks to NAT connection tracking, hands the reply back to `node2`.

### 2. The script's trick: `level6` reads `eth0`

Pulling strings out of the `level6` binary (built with **Nuitka**, so it's an ELF wrapping a
Python script `/src/level6.py`) with the `strings` substitute:

```bash
grep -a -oE '[[:print:]]{4,}' /path/level6
```

telling strings show up:

```
socket / AF_INET / SOCK_DGRAM / ioctl / fcntl   -> reads an interface's IP
eth0                                            -> ...and the interface is eth0 (hardcoded!)
10.0.0.2                                        -> the expected src
wrong host, sorry :(                            -> error if src doesn't match
ICMP / icmp / sr1 / timeout / resp              -> sends an ICMP and waits for a reply
Host {} seems unrecheable... sorry :(           -> error if no reply
192.168.123.                                    -> target (last octet built at runtime)
base64 / b64decode / ...ZstHVJN0Q...            -> target/flag obfuscated in base64
```

**Script logic:**
1. Reads the IP of `node2`'s **`eth0`** interface via `ioctl`.
2. If that IP is **not `10.0.0.2`** -> prints `wrong host, sorry :(` (or exits quietly).
3. Sends an **ICMP** packet (`sr1`) to `192.168.123.1` and waits for a reply.
4. If no reply -> `Host 192.168.123.1 seems unrecheable... sorry :(`.

This is the core of the trick: **the script is wired to read `eth0`.** So on `node2` the IP
`10.0.0.2` has to sit on **`eth0`**, not on any other interface, even though the ping would work
from any interface on the right network.

### The two constraints together

Both must hold at once:

- **Script constraint:** `10.0.0.2` on `node2-eth0`.
- **Physical constraint:** `node2-eth0` has to be the cable end connected to `node1`, and `node1` must have `10.0.0.1` on the twin end.

The `@ifNN` check in recon is what confirms these two line up (node2-`eth0` <-> node1-`eth1`). If
`make up` had wired `node2-eth0` to `node3`, the topology would be different and would need extra
thought.

## Exploit, step by step

### Prerequisite: the `iptable_nat` kernel module

In the containers the iptables `nat` table is often unavailable: the first `iptables -t nat`
command answers with

```
can't initialize iptables table `nat`: Table does not exist (do you need to insmod?)
```

The `nat` table comes from the **`iptable_nat`** kernel module. Since containers **share the host
kernel**, the module has to be loaded **on the host**, not in the container (`modprobe` isn't even
present in the container).

On the host (becoming root with `su -` if `sudo` isn't available):

```bash
modprobe iptable_nat
lsmod | grep -E 'iptable_nat|nf_nat'   # verify
```

Once loaded on the host, the `nat` table becomes usable **inside all containers**.

### node1 (the gateway / NAT)

```bash
docker exec -it downloads-node1-1 /bin/bash

# eth0 already has 192.168.123.123; assign 10.0.0.1 to the node2 side (eth1, twin of node2-eth0)
ip addr add 10.0.0.1/24 dev eth1
ip link set eth1 up

# MASQUERADE: mask packets from 10.0.0.0/24 leaving via eth0 (192.168.123 side)
iptables -t nat -A POSTROUTING -o eth0 --source 10.0.0.0/24 -j MASQUERADE

iptables -t nat -L POSTROUTING -n -v   # check the rule
```

On `-o eth0`: `-o` is the **outbound** interface. `node2`'s packet **enters** `node1` on `eth1`
and **leaves** toward the destination on `eth0`. POSTROUTING looks at the packet just before it
leaves the machine, so the right device is the exit one (`eth0`), not the entry one.

### node2 (the client)

```bash
docker exec -it downloads-node2-1 /bin/bash

# 10.0.0.2 MUST go on eth0 (the interface level6 reads)
ip addr add 10.0.0.2/24 dev eth0
ip link set eth0 up

# route to the destination network, via gateway node1
ip route add 192.168.123.0/24 via 10.0.0.1
```

### Verify and flag

```bash
ping -c 2 10.0.0.1        # node2 <-> node1 link (must answer)
ping -c 2 192.168.123.1   # end-to-end: works thanks to NAT
level6                    # prints the flag
```

Useful detail in the ping to `192.168.123.1`: the **`ttl=63`** (started at 64, decremented by 1)
confirms the packet crossed **one hop**, so it was routed and masqueraded by `node1`. The `pkts`
counter on the `MASQUERADE` line of `iptables -t nat -L -v` also increments, proof the NAT is
actually working.

## Flag

```
CCIT{****************}
```

## What I learned

- A route only teaches the outbound direction: if the remote host can't answer my network, the
  reply is lost and you need the MASQUERADE.
- The veth `@ifNN` indices change on every `make up`. I trusted a mapping from an earlier session
  and had `eth0`/`eth1` swapped, about twenty minutes wasted before reverifying them.
- `level6` read the IP from `eth0` hardcoded: without pulling the strings I'd never have guessed
  it, I'd have just tried at random.
- In containers the NAT modules (`iptable_nat`) load on the host: the kernel is shared, `modprobe`
  isn't even in the container.
- `-o` in POSTROUTING is the outbound interface, not the inbound one.